# Soundfonts

Soundfonts (`.sf2` / `.sf3`) are not committed to this repo — they are
typically large (30-300 MB) and often license-encumbered. Instead this
folder is the *expected* location: drop a soundfont here and
`scripts/render_audio.py` will find it.

## Recommended free soundfonts

- **FluidR3_GM.sf2** (140 MB, Creative Commons / MIT-style permissive)
  — the canonical free GM soundfont. Good flute, pan-flute, and string
  presets. Search the web for "FluidR3_GM.sf2 download" — there are
  multiple mirrors.

- **GeneralUser GS** (30 MB, free for commercial use with attribution)
  — smaller than FluidR3, slightly cleaner balance. Available from
  S. Christian Collins' site.

- **Sonatina Symphonic Orchestra** (varies, CC license) — bigger,
  realistic strings and woodwinds. Useful for violin, harp, clarinet
  arrangements.

For renders that match Tony's specific instrument builds, future
versions of this repo will host hand-recorded samples mapped to a
custom soundfont. v0.1 uses GM fallbacks (see
`references/audio-rendering.md` for the GM preset table).

## Where else `render_audio.py` looks

In order, until it finds a soundfont:

1. `assets/soundfonts/` (this folder)
2. `/usr/share/sounds/sf2/` (Linux distro packages)
3. `/usr/share/soundfonts/` (alternate Linux convention)
4. `~/soundfonts/`

Override with `--soundfont /path/to/file.sf2`.

## Why not commit a soundfont?

- Size: bloats clones for users who already have one.
- Licensing: most "free" soundfonts have specific attribution or
  redistribution terms that would attach to this repo.
- Substitutability: any GM-compliant soundfont works. The user can
  pick whichever they prefer.

The `.gitignore` excludes `*.sf2` and `*.sf3` everywhere except this
README.
