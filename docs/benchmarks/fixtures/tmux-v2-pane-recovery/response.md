# tmux-v2 Recovery Plan

Report pane liveness first: session name, window, pane id, active command, and whether the pane is idle, running, or waiting for input.

For a Codex pane that stopped at a shell prompt, recover with tmux send-keys and a scoped codex resume command for that persona lane. Keep the original sprint handoff visible in the pane history when possible.

Safety: this is operational recovery only. Do not reset, restore, checkout, or otherwise rewrite shared repo state. If a pane is sitting inside a shared repo, record that fact in the liveness report and ask the persona to continue from its own worktree.
