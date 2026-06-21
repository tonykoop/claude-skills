# Tailscale Webhook Dispatch

Design and setup guide for Story #412 (Epic #406). Enables the mobile→home-PC
dispatch leg of the autonomous idea pipeline: a clip captured on the phone
triggers `inbox_watcher.py`, which POSTs a signed dispatch payload to a tiny
HTTP listener on the home PC over Tailscale. The home PC then runs the
`gemini_to_github.py` stage without any manual login.

---

## Architecture

```
[Mobile device — Tailscale peer]                 [Home PC — Tailscale peer]
  Obsidian inbox watcher                           Webhook listener (port 19420)
  (inbox_watcher.py)                               (tailscale_dispatch.py --serve)
        |                                                   |
        | POST /dispatch  (HMAC-SHA256 signed)             |
        |  ─────────────────────────────────────────────►  |
        |                                               validates HMAC
        |                                               runs pipeline_cmd
        |  ◄─────────────────────────────────────────────  |
        |  200 OK / 401 Unauthorized / 400 Bad Request      |
```

Both peers must be on the same Tailscale tailnet. No ports need to be opened
on the public internet — Tailscale handles the encrypted overlay.

---

## Prerequisites

1. **Tailscale installed** on both the mobile (Android/iOS via Tailscale app) and
   the home PC (WSL2 or Windows host).
2. The home PC's Tailscale IP or MagicDNS name is stable and known (e.g.
   `100.x.x.x` or `my-pc.tailnet.ts.net`).
3. A shared HMAC secret is generated once and stored **out of the URL** on both
   sides (see Token setup below).

### Tailscale MagicDNS

Tailscale MagicDNS gives each machine a stable hostname like `tony-pc.ts.net`.
Use this instead of the numeric IP so the mobile shortcut does not break when
Tailscale reassigns the IP:

```
# On home PC — check your MagicDNS hostname
tailscale status | head -5
```

---

## Token / secret setup

The HMAC secret is a shared key. It is **never** put in the request URL (only in
the `X-Dispatch-Signature` header).

### Generating the secret

```bash
python -c "import secrets; print(secrets.token_hex(32))"
# e.g. a3f8...  (64 hex chars)
```

### Storing the secret

**Home PC (server side):**

```bash
# Store in an environment variable or a file outside the repo
export DISPATCH_SECRET="a3f8..."
# Or add to ~/.profile / ~/.bashrc
```

**Mobile side:**

Store the same secret in the iOS Shortcut or Android Tasker profile. Use the
"Get Contents of URL" action's custom headers field:

```
X-Dispatch-Signature: <computed HMAC — see mobile bridge doc>
```

Since mobile platforms cannot easily run Python for HMAC, the recommended
approach is to use the pre-signed dispatch via the desktop `tailscale_dispatch.py
--dispatch` command, which computes the HMAC and POSTs in one step. Run this from
WSL2 via SSH-over-Tailscale rather than computing HMAC on the phone.

---

## Server setup (home PC)

```bash
# Start the webhook listener
python plugins/maker/skills/idea-incubator/scripts/tailscale_dispatch.py \
  --serve \
  --host 0.0.0.0 \
  --port 19420 \
  --secret-env DISPATCH_SECRET \
  --pipeline-cmd "python /path/to/gemini_to_github.py --inbox {inbox_path} --mode {mode}"
```

| Flag | Default | Notes |
|---|---|---|
| `--host` | `127.0.0.1` | Use `0.0.0.0` to accept from any Tailscale peer |
| `--port` | `19420` | Arbitrary; avoid well-known ports |
| `--secret-env` | — | Name of env var holding the HMAC secret |
| `--pipeline-cmd` | — | Command template; `{inbox_path}` and `{mode}` are substituted |

Keep this running as a systemd service or via tmux so it survives reconnects.

### Systemd unit (optional)

```ini
[Unit]
Description=Idea incubator dispatch webhook

[Service]
ExecStart=python /path/to/tailscale_dispatch.py --serve --host 0.0.0.0 --port 19420 --secret-env DISPATCH_SECRET --pipeline-cmd "python /path/to/gemini_to_github.py --inbox {inbox_path}"
Environment=DISPATCH_SECRET=<your-secret>
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

---

## Security model

| Property | How enforced |
|---|---|
| Confidentiality | Tailscale WireGuard overlay — in-transit encryption, no plaintext on wire |
| Authentication | HMAC-SHA256 of `method + "\n" + path + "\n" + body` with shared secret |
| Replay protection | `X-Dispatch-Timestamp` header must be within ±5 minutes of server clock; server maintains a nonce set for the window |
| Authorization | Only devices on the same tailnet can reach the listener; ACL rules further restrict which peers may connect |

### Signature computation

```
sig = HMAC-SHA256(secret, f"POST\n/dispatch\n{json_body}")
header: X-Dispatch-Signature: sha256={hex(sig)}
```

The server re-derives the same signature and compares with `hmac.compare_digest`
(constant-time) to prevent timing attacks.

### ACL recommendation

In the Tailscale admin console, add an ACL rule that restricts port 19420 to
only the mobile device's Tailscale IP:

```json
{
  "action": "accept",
  "src": ["tag:mobile"],
  "dst": ["tag:home-pc:19420"]
}
```

---

## Dispatch payload schema

```json
{
  "inbox_path": "/absolute/path/to/obsidian/00-inbox/gemini-abc123-brainstorm.md",
  "mode": "APPEND",
  "trigger": "incubate this",
  "conversation_id": "gemini-abc123-brainstorm"
}
```

- `inbox_path`: absolute path on the **home PC** filesystem (not the mobile path)
- `mode`: `"CREATE"` or `"APPEND"` — from `append_mode.detect_mode()`
- `trigger`: the verbal trigger phrase that fired the watcher (for logging)
- `conversation_id`: the stable filename stem derived by `url_upsert.sanitize_chat_url()`

---

## Dispatch from the command line (test)

```bash
python tailscale_dispatch.py --dispatch \
  --host 100.x.x.x \
  --port 19420 \
  --secret-env DISPATCH_SECRET \
  --payload-json '{"inbox_path":"/tmp/test.md","mode":"CREATE","trigger":"test","conversation_id":"test-1"}'
```

A 200 response confirms the server accepted and queued the pipeline run.

---

## Failure handling

| Failure | Behavior |
|---|---|
| HMAC mismatch | Server returns 401; dispatch is silently dropped on the server side; `--dispatch` prints error and exits non-zero |
| Timestamp out of window (>5 min skew) | Server returns 400; check NTP sync on mobile |
| Server unreachable (Tailscale down) | `--dispatch` raises `urllib.error.URLError`; watcher logs the error and retries on next scan cycle |
| Pipeline command fails | Server returns 200 (the webhook accepted the payload); pipeline stderr is written to server log |

The webhook is fire-and-forget from the mobile side. The home PC's pipeline log
is the authoritative record of what ran.

---

## See also

- [mobile-capture-bridge.md](mobile-capture-bridge.md) — iOS/Android clip setup
- [gemini-export-pipeline.md](gemini-export-pipeline.md) — overall pipeline stages
- [`scripts/tailscale_dispatch.py`](../scripts/tailscale_dispatch.py) — implementation
