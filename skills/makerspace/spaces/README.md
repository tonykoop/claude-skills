# Spaces

Each makerspace this skill knows about lives in its own folder here.
A folder is one **space profile**: a `profile.yaml` plus a few markdown
attachments.

## What's here

| Folder | Purpose |
|--------|---------|
| `_template/` | Schema-demonstrating template. Copy this to start a new space. |
| `home-shop-default/` | Generic fallback when the user names no specific shop. |
| `maker-nexus/` | Seed profile — Maker Nexus, Sunnyvale, CA. |

## Adding your makerspace

```bash
cp -r _template <your-shop-slug>
cd <your-shop-slug>
# Edit profile.yaml — fill every "REQUIRED" field
# Edit tools.md, materials-policy.md, certifications.md,
# classes.md, safety-rules.md as far as you have content.
```

Then either:

- **Use it locally.** The skill picks up new folders automatically.
  Reference your space by slug: "I'm at `<your-shop-slug>`."
- **Submit a PR.** Other members of your space (or curious makers
  elsewhere) can use the same profile. Mark `visibility: private` in
  the profile if it contains member-only content.

## What "good" looks like

A complete profile has:

- Every `# REQUIRED` field in `profile.yaml` filled in.
- A `tools.md` with at least the major machines.
- A `materials-policy.md` with the explicit bans (most makerspaces
  have a few — chlorinated plastics on lasers is universal).
- A `certifications.md` if your space has a cert system, even if it's
  informal.
- A `classes.md` if your space runs classes — at minimum the classes
  that grant tool access.
- A `safety-rules.md` summarizing PPE expectations.

You don't need all of these to start. A profile with just
`profile.yaml` + `tools.md` is already useful — the skill plans
better with a real tool list than with assumptions.

## Schema reference

See `references/space-profile-schema.md` (one level up) for the full
field-by-field schema documentation.

## Privacy and visibility

Profiles default to `visibility: public`. Mark a profile as
`visibility: private` if its contents include:

- Member-only documents (instructor names, internal incident reports)
- Equipment passwords or access codes
- Information your shop hasn't approved for public release

Private profiles work the same way for the user but the skill won't
suggest sharing them and won't include them in any public artifact.

## Updating an existing profile

If your shop adds a new tool, retires an old one, or changes a
material policy, edit the profile directly. The skill always reads
the current state, so a fresh git pull is enough.

If your shop runs DokuWiki, `scripts/scrape_maker_nexus.py` (which
will work for most DokuWiki shops with minor parser tweaks) can
re-scrape the equipment page and merge into the existing profile.

## What this isn't

- It isn't a substitute for your shop's actual onboarding. Don't
  walk into a shop assuming the profile here is current — verify
  with shop staff before running anything.
- It isn't a real-time reservation system. The `reservation_url` in
  a tool entry points to wherever your shop's actual reservation
  system lives.
- It isn't the skill's training data. The profile is read at use
  time, not baked into model weights. Update it freely.
