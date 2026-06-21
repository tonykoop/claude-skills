#!/usr/bin/env python3
"""Tailscale webhook dispatch for the idea-incubator pipeline.

Story #412 (Epic #406). Two roles in one script:

**Server** (``--serve``):
  A tiny ``socketserver.TCPServer`` that listens for signed dispatch POSTs from
  the mobile watcher and runs the configured pipeline command.  All validation
  happens before any subprocess is spawned.

**Client** (``--dispatch``):
  Signs a dispatch payload with HMAC-SHA256 and POSTs it to the server. Designed
  to run from a desktop/CI context where the secret is available as an env var.

Security model
--------------
* HMAC-SHA256 over ``METHOD + "\\n" + PATH + "\\n" + BODY`` with a shared secret
  that lives only in env vars — never in a URL or command-line argument.
* ``hmac.compare_digest`` for constant-time comparison.
* Timestamp header must be within ±300 s of server clock (replay guard).
* Nonce cache: server rejects a (timestamp, nonce) pair seen within the window.

Design constraints
------------------
* Stdlib only — no external deps.
* ``subprocess.run`` with a list (no ``shell=True``) to prevent injection.
* Payload is JSON; pipeline_cmd may use ``{inbox_path}`` and ``{mode}``
  placeholders that are str.format-expanded safely.
"""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import hmac
import http.server
import json
import os
import queue
import socketserver
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Callable

# ---------------------------------------------------------------------------
# Payload
# ---------------------------------------------------------------------------

_DISPATCH_PATH = "/dispatch"
_SIG_HEADER = "X-Dispatch-Signature"
_TS_HEADER = "X-Dispatch-Timestamp"
_NONCE_HEADER = "X-Dispatch-Nonce"
_REPLAY_WINDOW_S = 300  # ±5 minutes


@dataclasses.dataclass
class DispatchPayload:
    """Structured payload sent from watcher to home-PC listener."""

    inbox_path: str
    mode: str  # "CREATE" or "APPEND"
    trigger: str
    conversation_id: str

    def to_json(self) -> str:
        return json.dumps(dataclasses.asdict(self), sort_keys=True)

    @classmethod
    def from_json(cls, data: str) -> "DispatchPayload":
        d = json.loads(data)
        return cls(
            inbox_path=d["inbox_path"],
            mode=d["mode"],
            trigger=d.get("trigger", ""),
            conversation_id=d.get("conversation_id", ""),
        )


# ---------------------------------------------------------------------------
# Signing
# ---------------------------------------------------------------------------


def _sig_message(method: str, path: str, body: bytes) -> bytes:
    return f"{method}\n{path}\n".encode() + body


def sign_payload(secret: str, method: str, path: str, body: bytes) -> str:
    """Return hex HMAC-SHA256 of method+path+body."""
    mac = hmac.new(secret.encode(), _sig_message(method, path, body), hashlib.sha256)
    return mac.hexdigest()


def verify_signature(secret: str, method: str, path: str, body: bytes, sig_hex: str) -> bool:
    """Constant-time comparison; returns False if sig is missing or wrong."""
    if not sig_hex:
        return False
    expected = sign_payload(secret, method, path, body)
    return hmac.compare_digest(expected, sig_hex)


# ---------------------------------------------------------------------------
# Nonce cache (simple in-memory replay guard)
# ---------------------------------------------------------------------------


class _NonceCache:
    def __init__(self, window_s: int = _REPLAY_WINDOW_S) -> None:
        self._window = window_s
        self._seen: dict[str, float] = {}
        self._lock = threading.Lock()

    def seen(self, nonce: str, ts: float) -> bool:
        """Return True if this nonce was seen; record it if not."""
        now = time.time()
        with self._lock:
            # Evict expired entries first
            expired = [k for k, t in self._seen.items() if now - t > self._window * 2]
            for k in expired:
                del self._seen[k]
            if nonce in self._seen:
                return True
            self._seen[nonce] = ts
            return False


# ---------------------------------------------------------------------------
# HTTP handler
# ---------------------------------------------------------------------------


class WebhookHandler(http.server.BaseHTTPRequestHandler):
    """Handle a single POST /dispatch request."""

    # These are set by TailscaleWebhookServer before serving.
    server_secret: str = ""
    on_dispatch: Callable[[DispatchPayload], None] = lambda _: None
    nonce_cache: _NonceCache = _NonceCache()

    def log_message(self, fmt: str, *args: object) -> None:
        # Delegate to the server's logger to keep stdout clean.
        sys.stderr.write(f"[tailscale-dispatch] {fmt % args}\n")

    def do_POST(self) -> None:
        if self.path != _DISPATCH_PATH:
            self._reply(404, "not found")
            return

        # Read body
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        # Timestamp check
        ts_str = self.headers.get(_TS_HEADER, "")
        try:
            ts = float(ts_str)
        except ValueError:
            self._reply(400, "bad timestamp")
            return
        if abs(time.time() - ts) > _REPLAY_WINDOW_S:
            self._reply(400, "timestamp out of window")
            return

        # Nonce check
        nonce = self.headers.get(_NONCE_HEADER, "")
        if not nonce or self.nonce_cache.seen(nonce, ts):
            self._reply(400, "replay detected")
            return

        # HMAC check
        sig = self.headers.get(_SIG_HEADER, "")
        if not verify_signature(self.server_secret, "POST", _DISPATCH_PATH, body, sig):
            self._reply(401, "unauthorized")
            return

        # Parse payload
        try:
            payload = DispatchPayload.from_json(body.decode("utf-8"))
        except (json.JSONDecodeError, KeyError) as exc:
            self._reply(400, f"bad payload: {exc}")
            return

        # Dispatch asynchronously so we can return 200 immediately.
        t = threading.Thread(target=self.on_dispatch, args=(payload,), daemon=True)
        t.start()

        self._reply(200, "accepted")

    def _reply(self, code: int, message: str) -> None:
        body = message.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------


class TailscaleWebhookServer:
    """Thin wrapper around socketserver.TCPServer."""

    def __init__(
        self,
        host: str,
        port: int,
        secret: str,
        on_dispatch: Callable[[DispatchPayload], None],
    ) -> None:
        self._host = host
        self._port = port
        self._secret = secret
        self._on_dispatch = on_dispatch
        self._httpd: socketserver.TCPServer | None = None

    def start(self) -> None:
        secret = self._secret
        on_dispatch = self._on_dispatch
        cache = _NonceCache()

        class _Handler(WebhookHandler):
            server_secret = secret
            nonce_cache = cache

            def on_dispatch_impl(self, p: DispatchPayload) -> None:
                on_dispatch(p)

        _Handler.on_dispatch = staticmethod(on_dispatch)  # type: ignore[attr-defined]

        socketserver.TCPServer.allow_reuse_address = True
        self._httpd = socketserver.TCPServer((self._host, self._port), _Handler)
        sys.stderr.write(
            f"[tailscale-dispatch] serving on {self._host}:{self._port}\n"
        )
        self._httpd.serve_forever()

    def stop(self) -> None:
        if self._httpd:
            self._httpd.shutdown()


# ---------------------------------------------------------------------------
# Client dispatch
# ---------------------------------------------------------------------------


def send_dispatch(
    host: str,
    port: int,
    secret: str,
    payload: DispatchPayload,
    *,
    timeout: int = 10,
) -> bool:
    """POST a signed dispatch payload. Returns True on 200."""
    body = payload.to_json().encode("utf-8")
    ts = str(time.time())
    nonce = hashlib.sha256(os.urandom(16)).hexdigest()[:16]
    sig = sign_payload(secret, "POST", _DISPATCH_PATH, body)

    url = f"http://{host}:{port}{_DISPATCH_PATH}"
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            _SIG_HEADER: sig,
            _TS_HEADER: ts,
            _NONCE_HEADER: nonce,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status == 200
    except urllib.error.HTTPError as exc:
        sys.stderr.write(f"[tailscale-dispatch] server returned {exc.code}: {exc.reason}\n")
        return False
    except urllib.error.URLError as exc:
        sys.stderr.write(f"[tailscale-dispatch] connection error: {exc.reason}\n")
        return False


# ---------------------------------------------------------------------------
# Pipeline runner (called by server on each accepted dispatch)
# ---------------------------------------------------------------------------


def run_pipeline(pipeline_cmd_template: str, payload: DispatchPayload) -> None:
    """Expand placeholders in pipeline_cmd_template and run it."""
    cmd_str = pipeline_cmd_template.format(
        inbox_path=payload.inbox_path,
        mode=payload.mode,
        trigger=payload.trigger,
        conversation_id=payload.conversation_id,
    )
    # Shell-split safely — the template owner controls the fixed parts.
    import shlex
    args = shlex.split(cmd_str)
    sys.stderr.write(f"[tailscale-dispatch] running: {args}\n")
    result = subprocess.run(args, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        sys.stderr.write(
            f"[tailscale-dispatch] pipeline exited {result.returncode}:\n"
            f"{result.stderr}\n"
        )
    else:
        sys.stderr.write("[tailscale-dispatch] pipeline succeeded\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--serve", action="store_true", help="Run as webhook server.")
    mode_group.add_argument("--dispatch", action="store_true", help="Send a dispatch payload.")

    # Common
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind/connect (default: 127.0.0.1).")
    parser.add_argument("--port", type=int, default=19420, help="Port (default: 19420).")
    parser.add_argument(
        "--secret-env",
        default="DISPATCH_SECRET",
        help="Name of env var holding the HMAC secret (default: DISPATCH_SECRET).",
    )

    # Server-only
    parser.add_argument(
        "--pipeline-cmd",
        default="",
        help="Command template to run on each dispatch (server mode). {inbox_path} and {mode} are substituted.",
    )

    # Client-only
    parser.add_argument("--payload-json", default="", help="JSON dispatch payload string (client mode).")

    args = parser.parse_args(argv[1:])

    secret = os.environ.get(args.secret_env, "")
    if not secret:
        sys.stderr.write(f"error: env var {args.secret_env!r} is not set or empty\n")
        return 1

    if args.serve:
        pipeline_cmd = args.pipeline_cmd

        def on_dispatch(payload: DispatchPayload) -> None:
            if pipeline_cmd:
                run_pipeline(pipeline_cmd, payload)
            else:
                sys.stderr.write(
                    f"[tailscale-dispatch] received (no --pipeline-cmd): {payload}\n"
                )

        server = TailscaleWebhookServer(args.host, args.port, secret, on_dispatch)
        try:
            server.start()
        except KeyboardInterrupt:
            server.stop()

    elif args.dispatch:
        if not args.payload_json:
            sys.stderr.write("error: --payload-json required in dispatch mode\n")
            return 1
        try:
            payload = DispatchPayload.from_json(args.payload_json)
        except (json.JSONDecodeError, KeyError) as exc:
            sys.stderr.write(f"error: bad payload JSON: {exc}\n")
            return 1
        ok = send_dispatch(args.host, args.port, secret, payload)
        if ok:
            sys.stdout.write("dispatched\n")
        else:
            sys.stderr.write("dispatch failed\n")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
