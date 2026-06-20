"""Unit tests for the clip-harvester public client stub."""

from __future__ import annotations

import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# Inject the scripts/ directory so we can import without a package install.
_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(_SCRIPTS))

from clip_harvester import (  # noqa: E402
    ClipBackendResult,
    ClipHandoff,
    ClipNote,
    _serialise,
    call_asc_backend,
)

_DUMMY_NOTE = ClipNote(
    note_id="test-id-1",
    source_type="text_clip",
    captured_at="2026-06-20T00:00:00Z",
    raw_text="A test clip",
    tags=["test"],
)


class _MockServer:
    """Tiny in-process HTTP server for testing the backend client."""

    def __init__(self, status: int, body: dict) -> None:
        self._status = status
        self._body = body
        self._server: HTTPServer | None = None
        self._thread: threading.Thread | None = None

    def __enter__(self) -> str:
        status, body = self._status, json.dumps(self._body).encode()

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *_):
                pass

        self._server = HTTPServer(("127.0.0.1", 0), Handler)
        port = self._server.server_address[1]
        self._thread = threading.Thread(target=self._server.handle_request, daemon=True)
        self._thread.start()
        return f"http://127.0.0.1:{port}"

    def __exit__(self, *_):
        if self._server:
            self._server.server_close()


def test_no_backend_url_returns_unavailable(monkeypatch):
    monkeypatch.delenv("CLIP_HARVESTER_BACKEND_URL", raising=False)
    result = call_asc_backend(ClipHandoff(note=_DUMMY_NOTE))
    assert not result.available
    assert result.status == "unavailable"
    assert not result.succeeded


def test_backend_ok_response(monkeypatch):
    with _MockServer(200, {"status": "ok", "job_id": "j42", "output_url": "http://x"}) as url:
        monkeypatch.setenv("CLIP_HARVESTER_BACKEND_URL", url)
        result = call_asc_backend(ClipHandoff(note=_DUMMY_NOTE))
    assert result.available
    assert result.succeeded
    assert result.job_id == "j42"
    assert result.output_url == "http://x"


def test_backend_queued_response(monkeypatch):
    with _MockServer(200, {"status": "queued", "job_id": "j99"}) as url:
        monkeypatch.setenv("CLIP_HARVESTER_BACKEND_URL", url)
        result = call_asc_backend(ClipHandoff(note=_DUMMY_NOTE))
    assert result.available
    assert result.succeeded


def test_backend_http_error(monkeypatch):
    with _MockServer(500, {"error": "internal"}) as url:
        monkeypatch.setenv("CLIP_HARVESTER_BACKEND_URL", url)
        result = call_asc_backend(ClipHandoff(note=_DUMMY_NOTE))
    assert not result.available
    assert result.status == "error"
    assert "500" in result.message


def test_backend_unreachable(monkeypatch):
    monkeypatch.setenv("CLIP_HARVESTER_BACKEND_URL", "http://127.0.0.1:1")
    result = call_asc_backend(ClipHandoff(note=_DUMMY_NOTE))
    assert not result.available
    assert result.status == "error"


def test_serialise_includes_schema():
    d = _serialise(ClipHandoff(note=_DUMMY_NOTE, routing_hint="test"))
    assert d["schema"] == "asc-handoff-v1"
    assert d["routing_hint"] == "test"
    assert "note_id" in d["note"]


def test_clip_note_optional_fields_default():
    note = ClipNote(
        note_id="x",
        source_type="url_clip",
        captured_at="2026-06-20T00:00:00Z",
        raw_text="hi",
    )
    assert note.platform is None
    assert note.tags == []
    assert note.engagement == {}


def test_clip_backend_result_succeeded_false_when_unavailable():
    r = ClipBackendResult(available=False, status="unavailable")
    assert not r.succeeded


def test_clip_backend_result_succeeded_true_when_ok():
    r = ClipBackendResult(available=True, status="ok", job_id="j1")
    assert r.succeeded
