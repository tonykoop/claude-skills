# Promotion Handoff

Promotion means moving an incubated idea into a target repo, project board, or
specialist skill without losing the original issue trail.

## Handoff pattern

1. Restate the idea in one sentence.
2. Name the target repo or specialist skill.
3. Say what should exist when the handoff is done.
4. Link the source issue.
5. Include `closes #N` only when the downstream issue should close the source.

## Promote-batch / Cluster Mode

Use cluster mode when the user asks to promote a batch, when review surfaces a
capture cluster, or when GitHub search shows related captures instead of one
standalone idea.

Detect a cluster with any of these signals:

- Five or more related capture issues in a 48-hour window.
- Shared labels plus a common archive/source path, repo target, campaign,
  object name, project name, or downstream specialist.
- Sibling captures that block or clarify each other, such as inventory, media,
  CAD, provenance, and launch/publication follow-ups.

Before selecting one issue, produce a readiness matrix:

```markdown
## Promotion-readiness matrix

| Issue | State | Evidence | Blockers | Best next route | Decision |
|---|---|---|---|---|---|
| #<N> | open; labels | paths, counts, repo state, comments | missing owner decision, already done, missing assets, IP/provenance risk | repo or skill | promote, defer, close, comment |
```

Decision guidance:

- Promote the bounded candidate with enough evidence and an unblocked next
  action.
- Defer candidates that need an owner/repo decision, missing source assets, or
  upstream inventory.
- Comment rather than promote when the right action is to preserve provenance
  or connect sibling captures.
- Mark already-satisfied candidates explicitly so the user can close or archive
  them without creating duplicate work.

## Copy-pasteable handoff

```markdown
Promoting idea #<N> into <target>.

Source: #<N>
Summary: <one sentence>
Why now: <one sentence>
Related links: <issue links or URLs>

Requested output:
- <deliverable 1>
- <deliverable 2>

If the target work should close the source issue, use `closes #<N>` in the
downstream issue or PR body.
```

## Recovery/import evidence ledger

For legacy-import, archive recovery, CAD/media migration, or any promotion that
depends on files outside the issue text, add these fields to the promotion
output or downstream issue draft:

```markdown
## Provenance and source of truth

- Source issue: #<N>
- Source path or capture source: <path, URL, Telegram note, or unknown>
- Inventory evidence: <CSV/log/path plus row or search term>
- Copy/recovery evidence: <copy plan, robocopy/rsync log, checksum run, or none>
- Staged import path: <path or not staged>
- Observed file count/size/extensions: <facts only>
- Source-of-truth decision: <original archive, staged copy, repo, or unknown>
- Claims discipline: separate observed archive facts from inferred claims

## Import readiness

- Target repo exists: yes/no/unknown
- Initial visibility: private/public/unknown
- Git LFS needed before first import commit: yes/no/unknown
- LFS patterns to configure first: <patterns or none>
- First import commit should include: <files/directories>
- Source issue relationship: Refs #<N> or Closes #<N>
```

Ask the LFS question before any binary import when captures mention CAD, media,
ZIPs, PDFs, audio, video, large archives, or assets likely to exceed ordinary
Git hosting limits. Commit `.gitattributes` before adding the assets when the
answer is yes.

Use `Refs #<N>` when the source issue is still the provenance anchor. Use
`Closes #<N>` only when the downstream work fully satisfies the capture and the
user wants automatic closure.

## Worked example: Weather Balloon Camera Vessel

In the Round 7 archive-recovery cluster, several captures shared the same recent
source, labels, and aerial/legacy-import theme. A good cluster pass would rank:

```markdown
| Issue | State | Evidence | Blockers | Best next route | Decision |
|---|---|---|---|---|---|
| #53 full archive inventory | open/complete evidence | inventory already generated | already satisfied | comment/close | do not promote |
| #55 Weather Balloon Camera Vessel | open; capture/promote/maker | CAD folder, 46 files, 816.81 MB, .sldprt/.stl/.jpg/.eprt, staged copy | target repo absent; LFS needed | makerspace or maker-engineering | promote |
| #57 aerial print campaign | open capture | related campaign idea | repo/scope decision unclear | idea-incubator review | defer |
```

The #55 promotion should include provenance fields for the inventory CSV,
recovery/copy log, staged path, file count, extension counts, and source of
truth. It should ask for Git LFS before the first CAD import commit and use
`Refs #55` until the downstream repo contains the evidence ledger and import.

## Specialist pairings

- `maker-engineering` for fabrication and shop ideas.
- `instrument-maker-v4` for instrument concepts and acoustics.
- `yoga-sequencer` for class and sequence ideas.
- `skills-meta` for skill ecosystem or routing ideas.

## Ownership note

Do not hard-code future repo ownership or visibility in the handoff. Keep the
target repo as an explicit input unless the user has already chosen it.
