# Inbox Watcher Daemon Setup

Install guide for Story #409 (Epic #406). Covers running `inbox_watcher.py` as a
persistent background service that starts at login and restarts on failure — so
brainstorm clips land in GitHub issues "by the time you're back."

## Prerequisites

| Item | Notes |
|------|-------|
| Python 3.10+ | `python3 --version` |
| `gh` CLI authenticated | `gh auth status` |
| Obsidian vault synced to this machine | iCloud / Obsidian Sync / Syncthing |
| `claude-skills` repo cloned | Adjust paths in service files to match |

---

## macOS — launchd agent

Uses `scripts/com.tonykoop.inbox-watcher.plist`.

### 1. Edit paths in the plist

Open `scripts/com.tonykoop.inbox-watcher.plist` and adjust:

- `WorkingDirectory` → absolute path to the `scripts/` folder in your checkout
- The inbox argument (`/Users/tony/Inbound_Brainstorms`) → your vault's inbox folder
- `PATH` environment variable → add any custom tool locations (e.g. pyenv shim path)

If you use a virtualenv, replace `/usr/bin/python3` with the absolute venv interpreter path.

### 2. Install the agent

```bash
cp scripts/com.tonykoop.inbox-watcher.plist \
   ~/Library/LaunchAgents/com.tonykoop.inbox-watcher.plist

launchctl load ~/Library/LaunchAgents/com.tonykoop.inbox-watcher.plist
```

The daemon starts immediately and restarts at every login.

### 3. Verify it's running

```bash
launchctl list | grep inbox-watcher
# → PID <n>   0   com.tonykoop.inbox-watcher
tail -f /tmp/com.tonykoop.inbox-watcher.log
```

### 4. Stop / uninstall

```bash
launchctl unload ~/Library/LaunchAgents/com.tonykoop.inbox-watcher.plist
rm ~/Library/LaunchAgents/com.tonykoop.inbox-watcher.plist
```

### Troubleshooting (macOS)

| Symptom | Check |
|---------|-------|
| Exits immediately | `cat /tmp/com.tonykoop.inbox-watcher.err` |
| `gh` not found | Add brew prefix to `PATH` in the plist |
| `ModuleNotFoundError` | Use venv interpreter in `ProgramArguments` |

---

## Linux — systemd user service

Uses `scripts/inbox-watcher.service`.

### 1. Edit paths in the unit file

Open `scripts/inbox-watcher.service` and adjust `WorkingDirectory` if your checkout
is not at `~/code/claude-skills/...`. The `%h` expander resolves to your home
directory at runtime, so `%h/Inbound_Brainstorms` usually needs no change.

### 2. Install the user unit

```bash
mkdir -p ~/.config/systemd/user/
cp scripts/inbox-watcher.service ~/.config/systemd/user/

systemctl --user daemon-reload
systemctl --user enable --now inbox-watcher.service
```

### 3. Verify it's running

```bash
systemctl --user status inbox-watcher.service
journalctl --user -u inbox-watcher.service -f
```

### 4. Stop / uninstall

```bash
systemctl --user disable --now inbox-watcher.service
rm ~/.config/systemd/user/inbox-watcher.service
systemctl --user daemon-reload
```

### Enable lingering (optional — survive logout)

By default, user services stop when you log out. To keep the watcher alive on a
headless server:

```bash
loginctl enable-linger $USER
```

### Troubleshooting (Linux)

| Symptom | Check |
|---------|-------|
| Unit fails to start | `journalctl --user -u inbox-watcher.service -n 50` |
| `python3` not found | `which python3` → update `ExecStart` path |
| Inbox dir missing | `mkdir -p ~/Inbound_Brainstorms` |

---

## Daemon behaviour summary

| Behaviour | Detail |
|-----------|--------|
| Poll interval | 10 s (adjust `--interval` in the service file) |
| Trigger check | ON by default — only fires on verbal-trigger phrases (see `inbox_watcher.py`) |
| Idempotency | `.dispatched` sidecar prevents re-dispatch across restarts |
| Pipeline command | `python -m gemini_to_github {file}` (default) — override with `--pipeline-cmd` |
| Restart on crash | launchd: `KeepAlive true`; systemd: `Restart=on-failure`, 30 s back-off |

---

## References

- `scripts/inbox_watcher.py` — polling daemon source (Story #409)
- `scripts/com.tonykoop.inbox-watcher.plist` — macOS launchd agent
- `scripts/inbox-watcher.service` — Linux systemd user unit
- `references/mobile-capture-bridge.md` — how files land in the inbox (Story #407)
- `references/tailscale-dispatch.md` — remote wake via Tailscale (Story #412)
