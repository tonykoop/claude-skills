# Agent Sandbox Isolation for Tool-Executing Subagents

**Origin capture:** tonykoop/claude-skills#392 (2026-06-20)

## Core requirement

Subagents that run shell commands, CAD CLIs, or deploy scripts should execute inside a hardened sandbox with an explicit, serializable workspace-state accumulator — not inside the shared host workspace. As the sprint grid starts driving real tools (OpenSCAD, bash scripts, deploys), blast-radius isolation becomes a mandatory safety control.

## Sandbox options

### Option A: Docker-in-Docker (DinD)

- Each subagent gets a fresh container with the tool pre-installed
- The container's `/workspace` is mapped from a per-agent directory on the host
- On agent exit, the workspace directory is the only persistent artifact
- Failures are contained to the container; the host filesystem is read-only from inside

**Trade-offs:** +portable, +easy to audit the filesystem diff; −Docker daemon overhead (~200–500ms startup), −requires `--privileged` or rootless Docker

### Option B: Firecracker microVMs

- Each subagent gets a dedicated microVM (128MB RAM minimum; boots in ~125ms)
- The microVM mounts a shared read-only rootfs + a per-agent read-write overlay
- The overlay diff is serialized as a JSON workspace-state accumulator on shutdown
- Network access is gated by the VM's virtio-net interface (can be disabled entirely)

**Trade-offs:** +strongest isolation, +deterministic teardown; −setup complexity, −requires Linux kernel with KVM support (WSL2 has KVM via msft kernel since 6.6)

### Option C: Lightweight namespace isolation (current baseline)

- Use Linux namespaces (mount + network + PID) via `unshare` or `bubblewrap`
- No container daemon needed; low overhead
- Partial blast-radius control: prevents most accidental side effects but not all

**Trade-offs:** +zero-daemon overhead; −weaker than DinD or Firecracker, −less portable on non-Linux hosts

## Workspace-state accumulator design

Regardless of sandbox backend, the agent's state should be serializable:

```json
{
  "agent_id": "agent-42",
  "sandbox_type": "dind",
  "started_at": "2026-06-21T03:00:00Z",
  "workspace_diff": {
    "created": ["output/result.stl", "output/design.scad"],
    "modified": ["config/params.json"],
    "deleted": []
  },
  "exit_code": 0,
  "stdout_tail": "...last 500 chars...",
  "stderr_tail": ""
}
```

This accumulator is written to `/tmp/agents/<agent_id>/state.json` and can be collected by the sprint supervisor for audit and merge decisions.

## Relationship to existing skills

| Existing skill | Overlap | What sandbox adds |
|----------------|---------|-------------------|
| `verification-gates` | Runs repeatable commands and checks output | Containment — gates run inside sandbox so failures don't touch shared workspace |
| `run-swarm` (internal) | Orchestrates parallel agent dispatch | Per-agent workspace isolation instead of shared git working tree |
| `sprint-supervisor` | Monitors pane state | Workspace-state accumulator gives supervisor a structured view of what changed |

## Promotion path

1. Evaluate whether `bubblewrap` namespace isolation is sufficient for the current tool set (OpenSCAD, gh CLI, bash scripts)
2. If blast-radius incidents occur: promote to DinD backend with per-agent container
3. If KVM available on WSL2 host: evaluate Firecracker for the highest-trust agents (deploys, smart-contract interactions)

## Links

- Related: wrfcoin/smart-contracts #134 (safe-paperclip circuit-breakers)
- Related: StudioPipeline #76 (render sandbox)
- See also: `verification-gates` skill, `sprint-supervisor` skill
