Deploy latest code to the testnet node(s).

By default deploys to **both** the remote testnet node (a Proxmox host running an LXC container) and the local desktop node (Docker on the dev machine). The remote target's IP and CT ID are configured via environment variables — see `deploy-node.sh` for the env-var contract or set them at the top of the script.

Run the deploy-node script:

```bash
./.claude/commands/deploy-node.sh
```

Supports flags:
- `--target n5|desktop|both` — pick a target (default: both)
- `--pull-only` — just pull code, don't rebuild or restart
- `--skip-build` — pull and restart without rebuilding images
- `--restart` — just restart the stack
- `--status` — check current service health on both targets

Report which repos were updated, build success/failure, and service health status.

## Configuration

Set these environment variables before running (or in a `.env` file, or directly at the top of `deploy-node.sh`):

| Variable | Default | Purpose |
|---|---|---|
| `PROXMOX_HOST` | `root@<your-host>` | SSH target for the remote node's Proxmox hypervisor (e.g. `root@192.168.1.10`) |
| `CT_ID` | `101` | Proxmox LXC container ID running the testnet node |
| `N5_SRC_DIR` | `/home/<user>/wrfcoin-src` | Path inside the LXC container where the source repos are checked out |
| `N5_COMPOSE_DIR` | `$N5_SRC_DIR/infra/testnet` | Path to the docker-compose stack inside the container |
| `DESKTOP_SRC_DIR` | `/home/<user>/wrfcoin` | Path on the dev machine where source repos are checked out |
| `DESKTOP_COMPOSE_DIR` | `$DESKTOP_SRC_DIR/infra/testnet` | Path to the local compose stack |

The actual production values for the wrfcoin testnet are kept private to the local workspace and not committed to this repo. The script ships with `<your-host>`-style placeholders that need real values before first use.
