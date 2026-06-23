"""Tests for tailscale_dispatch.py (Story #412 — Tailscale webhook dispatch)."""
import hashlib
import http.client
import json
import os
import subprocess
import sys
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from tailscale_dispatch import (
    DispatchPayload,
    TailscaleWebhookServer,
    _NonceCache,
    _REPLAY_WINDOW_S,
    _post_feedback_comment,
    run_pipeline,
    send_dispatch,
    sign_payload,
    verify_signature,
    WebhookHandler,
    _DISPATCH_PATH,
    _SIG_HEADER,
    _TS_HEADER,
    _NONCE_HEADER,
)


SECRET = "test-secret-abc123"
PAYLOAD = DispatchPayload(
    inbox_path="/tmp/test.md",
    mode="CREATE",
    trigger="incubate this",
    conversation_id="gemini-abc-1",
)


def _make_headers(body: bytes, *, secret: str = SECRET, ts_offset: float = 0.0) -> dict:
    """Build valid signed headers for a POST /dispatch request."""
    ts = str(time.time() + ts_offset)
    nonce = hashlib.sha256(os.urandom(16)).hexdigest()[:16]
    sig = sign_payload(secret, "POST", _DISPATCH_PATH, body)
    return {
        "Content-Type": "application/json",
        _SIG_HEADER: sig,
        _TS_HEADER: ts,
        _NONCE_HEADER: nonce,
    }


# ---------------------------------------------------------------------------
# Signing
# ---------------------------------------------------------------------------


class TestSignPayload(unittest.TestCase):
    def test_deterministic(self):
        body = b'{"x": 1}'
        s1 = sign_payload("secret", "POST", "/dispatch", body)
        s2 = sign_payload("secret", "POST", "/dispatch", body)
        self.assertEqual(s1, s2)

    def test_different_secret_different_sig(self):
        body = b'{"x": 1}'
        s1 = sign_payload("secret-a", "POST", "/dispatch", body)
        s2 = sign_payload("secret-b", "POST", "/dispatch", body)
        self.assertNotEqual(s1, s2)

    def test_different_body_different_sig(self):
        s1 = sign_payload("secret", "POST", "/dispatch", b"body-a")
        s2 = sign_payload("secret", "POST", "/dispatch", b"body-b")
        self.assertNotEqual(s1, s2)

    def test_different_method_different_sig(self):
        s1 = sign_payload("secret", "POST", "/dispatch", b"body")
        s2 = sign_payload("secret", "GET", "/dispatch", b"body")
        self.assertNotEqual(s1, s2)

    def test_returns_hex_string(self):
        sig = sign_payload("secret", "POST", "/dispatch", b"body")
        self.assertRegex(sig, r"^[0-9a-f]{64}$")


class TestVerifySignature(unittest.TestCase):
    def test_valid_sig_accepted(self):
        body = PAYLOAD.to_json().encode()
        sig = sign_payload(SECRET, "POST", "/dispatch", body)
        self.assertTrue(verify_signature(SECRET, "POST", "/dispatch", body, sig))

    def test_wrong_sig_rejected(self):
        body = PAYLOAD.to_json().encode()
        self.assertFalse(verify_signature(SECRET, "POST", "/dispatch", body, "badhex"))

    def test_empty_sig_rejected(self):
        body = PAYLOAD.to_json().encode()
        self.assertFalse(verify_signature(SECRET, "POST", "/dispatch", body, ""))

    def test_tampered_body_rejected(self):
        body = PAYLOAD.to_json().encode()
        sig = sign_payload(SECRET, "POST", "/dispatch", body)
        tampered = body + b"x"
        self.assertFalse(verify_signature(SECRET, "POST", "/dispatch", tampered, sig))


# ---------------------------------------------------------------------------
# Payload serialization
# ---------------------------------------------------------------------------


class TestDispatchPayload(unittest.TestCase):
    def test_roundtrip(self):
        j = PAYLOAD.to_json()
        p2 = DispatchPayload.from_json(j)
        self.assertEqual(p2.inbox_path, PAYLOAD.inbox_path)
        self.assertEqual(p2.mode, PAYLOAD.mode)
        self.assertEqual(p2.trigger, PAYLOAD.trigger)
        self.assertEqual(p2.conversation_id, PAYLOAD.conversation_id)

    def test_json_is_sorted(self):
        j = PAYLOAD.to_json()
        d = json.loads(j)
        self.assertEqual(list(d.keys()), sorted(d.keys()))

    def test_from_json_missing_optional_fields(self):
        j = json.dumps({"inbox_path": "/x", "mode": "APPEND"})
        p = DispatchPayload.from_json(j)
        self.assertEqual(p.trigger, "")
        self.assertEqual(p.conversation_id, "")

    def test_from_json_missing_required_raises(self):
        with self.assertRaises((KeyError, TypeError)):
            DispatchPayload.from_json(json.dumps({"mode": "CREATE"}))


# ---------------------------------------------------------------------------
# Nonce cache
# ---------------------------------------------------------------------------


class TestNonceCache(unittest.TestCase):
    def test_new_nonce_accepted(self):
        cache = _NonceCache(window_s=60)
        self.assertFalse(cache.seen("nonce-1", time.time()))

    def test_duplicate_nonce_rejected(self):
        cache = _NonceCache(window_s=60)
        ts = time.time()
        cache.seen("nonce-1", ts)
        self.assertTrue(cache.seen("nonce-1", ts))

    def test_different_nonces_accepted(self):
        cache = _NonceCache(window_s=60)
        ts = time.time()
        self.assertFalse(cache.seen("nonce-a", ts))
        self.assertFalse(cache.seen("nonce-b", ts))


# ---------------------------------------------------------------------------
# Live server (ephemeral port on 127.0.0.1)
# ---------------------------------------------------------------------------


class _LiveServer:
    """Spins up a real TailscaleWebhookServer on a random port for tests."""

    def __init__(self, secret: str = SECRET) -> None:
        self.received: list[DispatchPayload] = []
        self._evt = threading.Event()
        self._server = TailscaleWebhookServer(
            "127.0.0.1", 0, secret, self._on_dispatch
        )

    def _on_dispatch(self, payload: DispatchPayload) -> None:
        self.received.append(payload)
        self._evt.set()

    def __enter__(self) -> "_LiveServer":
        import socketserver

        socketserver.TCPServer.allow_reuse_address = True
        self._httpd = __import__("socketserver").TCPServer(
            ("127.0.0.1", 0),
            self._make_handler(),
        )
        self._port = self._httpd.server_address[1]
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()
        return self

    def _make_handler(self) -> type:
        received = self.received
        evt = self._evt
        secret = self._server._secret
        cache = _NonceCache()

        class H(WebhookHandler):
            server_secret = secret
            nonce_cache = cache

        def _on_dispatch(p: DispatchPayload) -> None:
            received.append(p)
            evt.set()

        H.on_dispatch = staticmethod(_on_dispatch)  # type: ignore[attr-defined]
        return H

    def __exit__(self, *_: object) -> None:
        self._httpd.shutdown()

    @property
    def port(self) -> int:
        return self._port

    def wait(self, timeout: float = 2.0) -> bool:
        return self._evt.wait(timeout)


class TestWebhookHandler(unittest.TestCase):
    def _post(
        self,
        port: int,
        body: bytes,
        headers: dict,
        path: str = _DISPATCH_PATH,
    ) -> tuple[int, str]:
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
        conn.request("POST", path, body=body, headers=headers)
        resp = conn.getresponse()
        return resp.status, resp.read().decode()

    def test_valid_dispatch_accepted(self):
        with _LiveServer() as srv:
            body = PAYLOAD.to_json().encode()
            hdrs = _make_headers(body)
            status, _ = self._post(srv.port, body, hdrs)
            self.assertEqual(status, 200)
            fired = srv.wait(timeout=2.0)
            self.assertTrue(fired)
            self.assertEqual(len(srv.received), 1)
            self.assertEqual(srv.received[0].inbox_path, PAYLOAD.inbox_path)

    def test_wrong_sig_returns_401(self):
        with _LiveServer() as srv:
            body = PAYLOAD.to_json().encode()
            hdrs = _make_headers(body)
            hdrs[_SIG_HEADER] = "0" * 64  # wrong sig
            status, _ = self._post(srv.port, body, hdrs)
            self.assertEqual(status, 401)
            # No dispatch fired
            fired = srv.wait(timeout=0.3)
            self.assertFalse(fired)

    def test_stale_timestamp_returns_400(self):
        with _LiveServer() as srv:
            body = PAYLOAD.to_json().encode()
            # Timestamp 10 minutes in the past
            hdrs = _make_headers(body, ts_offset=-(10 * 60))
            status, _ = self._post(srv.port, body, hdrs)
            self.assertEqual(status, 400)

    def test_wrong_path_returns_404(self):
        with _LiveServer() as srv:
            body = PAYLOAD.to_json().encode()
            hdrs = _make_headers(body)
            status, _ = self._post(srv.port, body, hdrs, path="/wrong")
            self.assertEqual(status, 404)

    def test_bad_json_returns_400(self):
        with _LiveServer() as srv:
            body = b"not-json"
            hdrs = _make_headers(body)
            status, _ = self._post(srv.port, body, hdrs)
            self.assertEqual(status, 400)


class TestSendDispatch(unittest.TestCase):
    def test_send_and_receive(self):
        with _LiveServer() as srv:
            ok = send_dispatch("127.0.0.1", srv.port, SECRET, PAYLOAD, timeout=5)
            self.assertTrue(ok)
            fired = srv.wait(timeout=2.0)
            self.assertTrue(fired)
            self.assertEqual(srv.received[0].mode, PAYLOAD.mode)

    def test_wrong_secret_returns_false(self):
        with _LiveServer() as srv:
            ok = send_dispatch("127.0.0.1", srv.port, "wrong-secret", PAYLOAD, timeout=5)
            self.assertFalse(ok)


class TestDispatchPayloadFeedbackFields(unittest.TestCase):
    """issue_num and repo fields on DispatchPayload (Story #412)."""

    def test_default_fields_empty(self):
        p = DispatchPayload(inbox_path="/x", mode="CREATE", trigger="t", conversation_id="c")
        self.assertEqual(p.issue_num, "")
        self.assertEqual(p.repo, "")

    def test_roundtrip_with_feedback_fields(self):
        p = DispatchPayload(
            inbox_path="/x", mode="CREATE", trigger="t", conversation_id="c",
            issue_num="42", repo="owner/repo",
        )
        p2 = DispatchPayload.from_json(p.to_json())
        self.assertEqual(p2.issue_num, "42")
        self.assertEqual(p2.repo, "owner/repo")

    def test_from_json_missing_feedback_fields_defaults_to_empty(self):
        j = json.dumps({"inbox_path": "/x", "mode": "APPEND"})
        p = DispatchPayload.from_json(j)
        self.assertEqual(p.issue_num, "")
        self.assertEqual(p.repo, "")


class TestPostFeedbackComment(unittest.TestCase):
    """_post_feedback_comment() — gh issue comment after pipeline success."""

    def _payload(self, issue_num: str = "99", repo: str = "owner/repo") -> DispatchPayload:
        return DispatchPayload(
            inbox_path="/tmp/test.md",
            mode="CREATE",
            trigger="incubate this",
            conversation_id="conv-abc",
            issue_num=issue_num,
            repo=repo,
        )

    def test_comment_posted_when_fields_set(self):
        captured: list = []

        def fake_run(cmd, **kwargs):
            captured.append(cmd)
            r = MagicMock()
            r.returncode = 0
            r.stderr = ""
            return r

        with patch("subprocess.run", side_effect=fake_run):
            _post_feedback_comment(self._payload())

        self.assertEqual(len(captured), 1)
        cmd = captured[0]
        self.assertIn("gh", cmd)
        self.assertIn("issue", cmd)
        self.assertIn("comment", cmd)
        self.assertIn("99", cmd)
        self.assertIn("-R", cmd)
        self.assertIn("owner/repo", cmd)

    def test_comment_skipped_when_issue_num_empty(self):
        with patch("subprocess.run") as mock_run:
            _post_feedback_comment(self._payload(issue_num=""))
            mock_run.assert_not_called()

    def test_comment_skipped_when_repo_empty(self):
        with patch("subprocess.run") as mock_run:
            _post_feedback_comment(self._payload(repo=""))
            mock_run.assert_not_called()

    def test_gh_failure_does_not_raise(self):
        def fake_run(cmd, **kwargs):
            r = MagicMock()
            r.returncode = 1
            r.stderr = "some error"
            return r

        with patch("subprocess.run", side_effect=fake_run):
            _post_feedback_comment(self._payload())  # must not raise

    def test_gh_missing_does_not_raise(self):
        with patch("subprocess.run", side_effect=FileNotFoundError("gh not found")):
            _post_feedback_comment(self._payload())  # must not raise


class TestRunPipelineFeedback(unittest.TestCase):
    """run_pipeline() posts comment on success, not on failure."""

    def _payload(self, issue_num: str = "7", repo: str = "org/repo") -> DispatchPayload:
        return DispatchPayload(
            inbox_path="/tmp/clip.md",
            mode="CREATE",
            trigger="incubate this",
            conversation_id="conv-1",
            issue_num=issue_num,
            repo=repo,
        )

    def _make_pipeline_result(self, returncode: int):
        r = MagicMock()
        r.returncode = returncode
        r.stdout = ""
        r.stderr = ""
        return r

    def test_comment_posted_after_successful_pipeline(self):
        comment_calls: list = []

        def fake_run(cmd, **kwargs):
            if "gh" in cmd:
                comment_calls.append(cmd)
                r = MagicMock(); r.returncode = 0; r.stderr = ""
                return r
            return self._make_pipeline_result(0)

        with patch("subprocess.run", side_effect=fake_run):
            run_pipeline("echo {inbox_path}", self._payload())

        self.assertEqual(len(comment_calls), 1)

    def test_comment_not_posted_after_failed_pipeline(self):
        comment_calls: list = []

        def fake_run(cmd, **kwargs):
            if "gh" in cmd:
                comment_calls.append(cmd)
            return self._make_pipeline_result(1)

        with patch("subprocess.run", side_effect=fake_run):
            run_pipeline("false", self._payload())

        self.assertEqual(len(comment_calls), 0)

    def test_comment_not_posted_when_no_issue_num(self):
        pipeline_ran = []

        def fake_run(cmd, **kwargs):
            pipeline_ran.append(cmd)
            return self._make_pipeline_result(0)

        with patch("subprocess.run", side_effect=fake_run):
            run_pipeline("echo {inbox_path}", self._payload(issue_num=""))

        # Only the pipeline itself ran — no gh comment
        self.assertEqual(len(pipeline_ran), 1)
        self.assertNotIn("gh", pipeline_ran[0])


if __name__ == "__main__":
    unittest.main()
