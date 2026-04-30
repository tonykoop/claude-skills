#!/usr/bin/env bash
# Deploy latest code to testnet nodes.
#
# Targets (both deploy by default):
#   - Remote (SSH → Proxmox host → LXC container running the node)
#   - Desktop (local Docker on this machine; WSL2)
#
# IMPORTANT: Configure the target host before first use. Either set env vars
# below before invoking, or edit the defaults at the top of this script.
# See deploy-node.md for the configuration contract.
#
# Usage:
#   ./deploy-node.sh                        # Full deploy to BOTH nodes
#   ./deploy-node.sh --target n5            # Remote only
#   ./deploy-node.sh --target desktop       # Desktop only
#   ./deploy-node.sh --target both          # Explicit both (same as default)
#   ./deploy-node.sh --pull-only            # Just pull, don't rebuild or restart
#   ./deploy-node.sh --skip-build           # Pull + restart, no rebuild
#   ./deploy-node.sh --restart              # Just restart the stack
#   ./deploy-node.sh --status               # Check current service health on both
#
# Flags can be combined, e.g.:
#   ./deploy-node.sh --target n5 --skip-build

set -uo pipefail

# ---- N5 (remote testnet node) config ---------------------------------------
# Override via environment or edit these defaults. The placeholder defaults
# will fail loudly so you don't accidentally run against the wrong host.
PROXMOX_HOST="${PROXMOX_HOST:-root@<your-proxmox-host>}"
CT_ID="${CT_ID:-101}"
N5_SRC_DIR="${N5_SRC_DIR:-/home/<user>/wrfcoin-src}"
N5_COMPOSE_DIR="${N5_COMPOSE_DIR:-$N5_SRC_DIR/infra/testnet}"
N5_COMPOSE_CMD="docker compose -f docker-compose.testnet.yml -f docker-compose.override.yml"

# ---- Desktop (local) config ------------------------------------------------
DESKTOP_SRC_DIR="${DESKTOP_SRC_DIR:-/home/<user>/wrfcoin}"
DESKTOP_COMPOSE_DIR="${DESKTOP_COMPOSE_DIR:-$DESKTOP_SRC_DIR/infra/testnet}"
# Desktop uses docker-compose v1 (hyphenated) + includes .desktop.yml override
DESKTOP_COMPOSE_CMD="docker-compose -f docker-compose.testnet.yml -f docker-compose.override.yml -f docker-compose.desktop.yml"
# Minimum peer-2 services (no monitoring / collectors)
DESKTOP_SERVICES=(postgres redis wrfcoin-node)

REPOS=(infra backend core4 frontend)

# ---- Sanity check placeholder values ---------------------------------------
if [[ "$PROXMOX_HOST" == *"<your-"* ]] || [[ "$N5_SRC_DIR" == *"<user>"* ]] || [[ "$DESKTOP_SRC_DIR" == *"<user>"* ]]; then
    cat >&2 <<'ERR'
deploy-node.sh: Configuration placeholders are still in place.

Set these before running (env vars or edit the script):
  PROXMOX_HOST   — e.g. root@192.168.1.10
  CT_ID          — e.g. 101
  N5_SRC_DIR     — path inside the LXC container where source is checked out
  DESKTOP_SRC_DIR — path on this machine where source is checked out

See claude/commands/deploy-node.md for the full configuration contract.
ERR
    exit 1
fi

# ---- Parse flags -----------------------------------------------------------
MODE="full"
TARGET="both"
while [ $# -gt 0 ]; do
    case "$1" in
        --pull-only)  MODE="pull-only"; shift ;;
        --skip-build) MODE="skip-build"; shift ;;
        --restart)    MODE="restart"; shift ;;
        --status)     MODE="status"; shift ;;
        --target)
            shift
            TARGET="${1:-}"
            case "$TARGET" in
                n5|desktop|both) ;;
                *) echo "Unknown --target: $TARGET (use n5|desktop|both)"; exit 1 ;;
            esac
            shift
            ;;
        --help|-h)
            sed -n '2,25p' "$0"
            exit 0
            ;;
        *)
            echo "Unknown flag: $1 (use --help for usage)"
            exit 1
            ;;
    esac
done

# ---- N5 helpers ------------------------------------------------------------
run_on_n5() {
    ssh -o ConnectTimeout=10 "$PROXMOX_HOST" "pct exec $CT_ID -- bash -c '$1'"
}

n5_reachable() {
    ssh -o ConnectTimeout=10 "$PROXMOX_HOST" "pct status $CT_ID" 2>/dev/null | grep -q running
}

# ---- Desktop helpers -------------------------------------------------------
run_on_desktop() {
    bash -c "cd $DESKTOP_COMPOSE_DIR && $1"
}

desktop_reachable() {
    [ -d "$DESKTOP_COMPOSE_DIR" ] && docker info >/dev/null 2>&1
}

# ---- Status path -----------------------------------------------------------
status_n5() {
    echo "=== Remote node ($PROXMOX_HOST CT $CT_ID) ==="
    if ! n5_reachable; then
        echo "  UNREACHABLE"
        return 1
    fi
    run_on_n5 "curl -sf http://localhost:8556/readyz >/dev/null 2>&1 && echo '  NODE:    OK' || echo '  NODE:    FAIL'"
    run_on_n5 "curl -sf http://localhost:4001/health >/dev/null 2>&1 && echo '  BACKEND: OK' || echo '  BACKEND: FAIL'"
    echo "  -- git state --"
    for repo in "${REPOS[@]}"; do
        branch=$(run_on_n5 "cd $N5_SRC_DIR/$repo && git rev-parse --abbrev-ref HEAD 2>/dev/null" 2>/dev/null || echo "?")
        sha=$(run_on_n5 "cd $N5_SRC_DIR/$repo && git rev-parse --short HEAD 2>/dev/null" 2>/dev/null || echo "?")
        printf "  %-12s %s @ %s\n" "$repo" "$branch" "$sha"
    done
}

status_desktop() {
    echo "=== Desktop (local, this machine) ==="
    if ! desktop_reachable; then
        echo "  UNREACHABLE (compose dir missing or docker daemon down)"
        return 1
    fi
    curl -sf http://localhost:8556/readyz >/dev/null 2>&1 && echo "  NODE:    OK" || echo "  NODE:    FAIL/NOT-RUNNING"
    echo "  -- peer count --"
    curl -s http://localhost:8556/network/info 2>/dev/null | grep -oE '"peer_count":[0-9]+' | head -1 || echo "  (node unreachable)"
    echo "  -- containers --"
    docker ps --filter name=wrfcoin-testnet --format "  {{.Names}}  {{.Status}}" 2>/dev/null | head -5
    echo "  -- git state --"
    for repo in core4 infra backend; do
        branch=$(git -C "$DESKTOP_SRC_DIR/$repo" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "?")
        sha=$(git -C "$DESKTOP_SRC_DIR/$repo" rev-parse --short HEAD 2>/dev/null || echo "?")
        printf "  %-12s %s @ %s\n" "$repo" "$branch" "$sha"
    done
}

if [ "$MODE" = "status" ]; then
    [ "$TARGET" = "n5" ] || [ "$TARGET" = "both" ] && status_n5
    [ "$TARGET" = "desktop" ] || [ "$TARGET" = "both" ] && { echo; status_desktop; }
    exit 0
fi

# ---- Deploy: Remote --------------------------------------------------------
deploy_n5() {
    echo "=== Remote deploy ($PROXMOX_HOST CT $CT_ID) ==="
    if ! n5_reachable; then
        echo "FAILED: Cannot reach Proxmox host or CT $CT_ID not running"
        return 1
    fi

    if [ "$MODE" != "restart" ]; then
        echo "-- pulling repos --"
        pull_failures=0
        for repo in "${REPOS[@]}"; do
            printf "  %-12s " "$repo"
            if output=$(run_on_n5 "cd $N5_SRC_DIR/$repo && git pull origin main 2>&1" 2>&1); then
                echo "$output" | tail -1
            else
                echo "FAILED: $output"
                pull_failures=$((pull_failures + 1))
            fi
        done
        [ "$pull_failures" -gt 0 ] && echo "WARNING: $pull_failures repo(s) failed to pull. Continuing..."
        [ "$MODE" = "pull-only" ] && { echo "Done (--pull-only)."; return 0; }
    fi

    if [ "$MODE" != "skip-build" ] && [ "$MODE" != "restart" ]; then
        echo "-- building --"
        if ! run_on_n5 "cd $N5_COMPOSE_DIR && $N5_COMPOSE_CMD build 2>&1"; then
            echo "FAILED: Docker build failed"
            return 1
        fi
    fi

    echo "-- restarting stack --"
    run_on_n5 "cd $N5_COMPOSE_DIR && $N5_COMPOSE_CMD up -d 2>&1" || echo "WARNING: compose up returned nonzero (likely readyz warmup; see verify below)"

    echo "-- verifying health --"
    max_attempts=24
    attempt=0
    node_ok=false
    backend_ok=false
    while [ $attempt -lt $max_attempts ]; do
        attempt=$((attempt + 1))
        $node_ok    || run_on_n5 "curl -sf http://localhost:8556/readyz"   >/dev/null 2>&1 && node_ok=true
        $backend_ok || run_on_n5 "curl -sf http://localhost:4001/health"   >/dev/null 2>&1 && backend_ok=true
        $node_ok && $backend_ok && break
        sleep 10
    done

    if $node_ok && $backend_ok; then
        echo "  NODE:    OK"
        echo "  BACKEND: OK"
    else
        $node_ok    || echo "  NODE:    NOT READY after $((max_attempts*10))s"
        $backend_ok || echo "  BACKEND: NOT READY after $((max_attempts*10))s"
        # Backend may not be running by design (depends_on node health). Try starting it.
        if ! $backend_ok; then
            echo "  -- attempting backend start (node may have become ready after compose-up) --"
            run_on_n5 "cd $N5_COMPOSE_DIR && $N5_COMPOSE_CMD up -d wrfcoin-backend 2>&1" | tail -3
            sleep 10
            run_on_n5 "curl -sf http://localhost:4001/health" >/dev/null 2>&1 && echo "  BACKEND: OK (after retry)" || echo "  BACKEND: still not healthy"
        fi
    fi
}

# ---- Deploy: Desktop -------------------------------------------------------
deploy_desktop() {
    echo "=== Desktop deploy (local, this machine) ==="
    if ! desktop_reachable; then
        echo "FAILED: compose dir missing or docker daemon down"
        return 1
    fi

    # Desktop pull happens via /pull-all at the workspace level.
    # deploy-node.sh on desktop does NOT pull individual repos — /pull-all is
    # the source of truth. We verify main is checked-out + up-to-date in core4,
    # infra, backend for the build to use latest code.
    if [ "$MODE" != "restart" ]; then
        echo "-- verifying desktop repos on main + up-to-date --"
        for repo in core4 infra backend; do
            branch=$(git -C "$DESKTOP_SRC_DIR/$repo" rev-parse --abbrev-ref HEAD 2>/dev/null)
            if [ "$branch" != "main" ]; then
                printf "  %-12s WARNING: on branch '%s' (not main) — build may be stale\n" "$repo" "$branch"
            else
                git -C "$DESKTOP_SRC_DIR/$repo" fetch origin main --quiet 2>&1 || true
                behind=$(git -C "$DESKTOP_SRC_DIR/$repo" rev-list --count HEAD..origin/main 2>/dev/null || echo "?")
                if [ "$behind" = "0" ]; then
                    printf "  %-12s main up-to-date\n" "$repo"
                else
                    printf "  %-12s WARNING: behind origin/main by %s commits (run /pull-all)\n" "$repo" "$behind"
                fi
            fi
        done
        [ "$MODE" = "pull-only" ] && { echo "Done (--pull-only)."; return 0; }
    fi

    if [ "$MODE" != "skip-build" ] && [ "$MODE" != "restart" ]; then
        echo "-- building ${DESKTOP_SERVICES[*]} --"
        if ! run_on_desktop "$DESKTOP_COMPOSE_CMD build ${DESKTOP_SERVICES[*]} 2>&1"; then
            echo "FAILED: Desktop docker build failed"
            return 1
        fi
    fi

    echo "-- restarting desktop stack --"
    run_on_desktop "$DESKTOP_COMPOSE_CMD up -d ${DESKTOP_SERVICES[*]} 2>&1" | tail -5

    echo "-- verifying --"
    sleep 10
    max_attempts=12
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        attempt=$((attempt + 1))
        if curl -sf http://localhost:8556/readyz >/dev/null 2>&1; then
            echo "  NODE:    OK (attempt $attempt)"
            peer_count=$(curl -s http://localhost:8556/network/info 2>/dev/null | grep -oE '"peer_count":[0-9]+' | head -1 || echo "?")
            echo "  $peer_count"
            return 0
        fi
        sleep 10
    done
    echo "  NODE: NOT READY after $((max_attempts*10))s — check \`docker logs wrfcoin-testnet-node --tail=30\`"
    return 1
}

# ---- Orchestrate -----------------------------------------------------------
OVERALL_STATUS=0
if [ "$TARGET" = "n5" ] || [ "$TARGET" = "both" ]; then
    deploy_n5 || OVERALL_STATUS=1
    echo ""
fi
if [ "$TARGET" = "desktop" ] || [ "$TARGET" = "both" ]; then
    deploy_desktop || OVERALL_STATUS=1
    echo ""
fi

echo "=== Deploy Summary ==="
[ "$TARGET" = "n5" ] || [ "$TARGET" = "both" ] && status_n5
[ "$TARGET" = "desktop" ] || [ "$TARGET" = "both" ] && { echo; status_desktop; }

exit $OVERALL_STATUS
