# Ableton handoff

When the user wants a polished audio render, a backing track, or a
project they can open in Ableton Live to keep working on, hand off to
the Ableton Claude connector (announced April 2026, alongside the
Adobe and Blender connectors — see
[anthropic.com/news/claude-for-creative-work](https://www.anthropic.com/news/claude-for-creative-work)).

The Ableton connector grounds Claude in Live and Push documentation,
enabling natural-language project building. As of mid-2026 it does not
expose direct `.als` write tools the way Adobe exposes document
rendering — instead, the user pastes a prompt into a Claude+Ableton
session and Claude builds the project interactively. This skill
prepares everything the user needs to make that paste effortless.

## When to use it

- The user asks for a "backing track" or "play-along."
- The user wants a polished audio mix (multiple instruments, reverb,
  compression).
- The user wants to take the tune somewhere — re-arrange, layer,
  remix — beyond what the local pipeline produces.
- The user wants the drone for a drone-flute or duduk arrangement
  rendered as a sustained pad rather than a single sample.

## What the skill produces for handoff

Stage the assets in the tune folder:

```
{tune}/
├── tune.abc
├── tune.musicxml      # Ableton imports MusicXML cleanly
├── tune.mid           # alternative input
├── ableton-prompt.md  # ready-to-paste prompt for the connector
└── notes.md
```

The `ableton-prompt.md` content follows this template:

```
I'd like to build an Ableton Live project for "{TITLE}" — a song
arranged for the {INSTRUMENT_DISPLAY_NAME} from Tony Koop's {REPO}
build. Please use this MIDI and MusicXML as the starting point:

[Attach: tune.mid, tune.musicxml]

Project requirements:
- Tempo: {TEMPO} bpm
- Key: {KEY}
- Time signature: {METER}

Tracks:
1. Melody — load a software instrument that approximates a
   {INSTRUMENT_TIMBRE_DESCRIPTION}. Set the MIDI clip from tune.mid.
2. {DRONE_TRACK_IF_APPLICABLE} — sustained tonic pad for the duration
   of the tune.
3. Metronome — quiet click on beats 1 and 3 (or whatever fits the
   meter) for practice.
4. Backing chord pad — root + fifth on each phrase boundary, low
   register, slow attack, long release. Use a soft pad sound.

Mix:
- Melody slightly in front (panned center, +0 dB).
- Drone bed -6 dB, panned center.
- Metronome -12 dB, panned right.
- Backing pad -8 dB, panned slightly left.

Add a slow plate reverb (1.5s decay, 20% wet) on the master bus.

Save the project as "{SLUG}.als" in the same folder as this prompt.
```

The placeholders (`{TITLE}`, `{INSTRUMENT_DISPLAY_NAME}`, etc.) get
filled in by `scripts/build_ableton_handoff.py` from the registry row
and the tune's ABC headers.

## Special cases by family

### Drone flutes (NAF, drone-flute, andean duct)

The drone *is* part of the instrument — but for practice, the user often
wants a drone track even when their flute doesn't physically produce one.
The Ableton handoff defaults to including a sustained tonic pad on
the second track. The `notes.md` for the tune mentions the drone choice.

### Duduk

Always include a *dam* drone track at the tonic pitch. Duduk tradition
expects this. Pad sound: warm, slightly buzzy double-reed; the
connector picks the closest available preset.

### Bagpipe-tradition arrangements (v0.2)

Drone bass and tenor drones at the chanter's tonic. No metronome —
bagpipe tradition is rubato within the bag's pressure. (When v0.2
ships full bagpipe support.)

### Strings (violin, harp, guitar)

Add a backing chord pad. For violin/harp, a sustained string-section
pad. For guitar, a soft piano or pad outlining the chord progression
written in the songsheet's `notes.md`.

### Percussion (pitched and unpitched)

For pitched percussion, treat as a single melody track. For unpitched,
the prompt template loads the pattern as a drum rack clip and adds a
basic ghost-hat track on offbeats for tempo grounding.

## Fallback (no Ableton connector)

If the user doesn't have the Ableton connector installed, the
`ableton-prompt.md` is still useful — they can:

- Open it in any DAW (Logic, FL Studio, Reaper, Cubase, Garageband)
  and follow the instructions manually.
- Paste it into a non-connector Claude session for general guidance.
- Use it as a planning document for their own arrangement work.

The MIDI + MusicXML are universal; only the `.als` writing depends on
Ableton specifically.

## What this skill does NOT do

- Render `.als` files directly. There is no public format for a
  third-party tool to write Ableton projects safely; the connector is
  the supported path.
- Substitute for live performance. The Ableton output is for practice
  and demos.
- Mix or master. The prompt template gives reasonable defaults but
  the user is expected to adjust per taste.
