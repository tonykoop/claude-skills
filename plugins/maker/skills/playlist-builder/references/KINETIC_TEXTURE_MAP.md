# Kinetic-Texture → Sonic Mapping

**Epic:** #471 — playlist-builder audio-dynamic  
**Story:** #474  
**Version:** v1.0  

---

## Overview

A choreography routine describes each block by its *kinetic texture* — the movement quality that
defines how the body moves through space. This document maps each kinetic texture to the sonic
qualities the playlist-builder uses when selecting tracks for that block.

The mapping is the selection oracle: `texture_map.py` reads this vocabulary to filter the catalog
before BPM matching runs.

---

## Core Texture Vocabulary

### `staccato`

**Movement quality:** Sharp, percussive, stop-start. Isolated pops, locks, hits against a beat.
Joints arrive at full extension and stop cleanly before the next impulse.

**Sonic targets:**
- Genres: minimal techno, industrial hip-hop, electro, neo-soul with tight quantisation
- Tags: `ticking`, `mechanical`, `staccato`, `glitchy`, `clipped`
- Audio qualities: short transients, heavy compression, prominent kick/snare attack, little reverb tail
- Avoid: lush pads, long reverb, legato strings, ambient washes

---

### `fluid`

**Movement quality:** Continuous, wave-like, no hard stops. Spine undulations, isolations that
roll through the body, slow level changes, contraction-release cycles.

**Sonic targets:**
- Genres: ambient, neo-classical, chill electronica, deep house (slow BPM range), lo-fi
- Tags: `pads`, `legato`, `ambient`, `evolving`, `warm`, `breathable`
- Audio qualities: long reverb/decay, slow-attack pads, continuous melodic lines, minimal percussion
- Avoid: heavy 4-on-the-floor kick, clipped transients, staccato synth stabs

---

### `tutting`

**Movement quality:** Angular, geometry-driven. Arms and hands move in 90° planes, forming
boxes and right-angle shapes. Rhythmically complex — layered independent arm/hand cadences
that contrast against each other.

**Sonic targets:**
- Genres: mid-tempo hip-hop, glitch-hop, polyrhythmic electronic, afrobeat
- Tags: `polyrhythmic`, `hi-hats`, `sub-bass`, `syncopated`, `layered`
- Audio qualities: prominent hi-hat patterns (triplet / swing grid), deep sub-bass that contrasts
  upper register, multiple independent rhythmic layers running simultaneously
- Avoid: straight 4/4 with no syncopation, heavy reverb wash

---

### `explosive`

**Movement quality:** Maximum-force, maximum-reach moments. Jumps, aerial catches, full-body
extensions that release built tension in a single beat.

**Sonic targets:**
- Genres: peak-hour techno, big-room house, drum and bass
- Tags: `peak`, `drop`, `high-energy`, `massive`, `build-release`
- Audio qualities: clear structural drop point, high energy, loud dynamic range, wide stereo
- Avoid: quiet ambient, minimalist tracks, sub-60 BPM

---

### `grounded`

**Movement quality:** Weight-downward. Stomps, foot-heavy polyrhythm, low centre of gravity,
plié-based or deep-squat transitions.

**Sonic targets:**
- Genres: afrobeat, cumbia, club-reggaeton, dancehall
- Tags: `bass-heavy`, `stomping`, `groove`, `low-end`, `rhythmic`
- Audio qualities: prominent low-frequency rhythm, call-and-response patterns, heavy kick pattern
- Avoid: treble-heavy tracks, high BPM without bass, delicate instrumentation

---

### `suspended`

**Movement quality:** Float, hover, weightlessness. Relevé balances, slow-motion sequences,
held poses that defy gravity.

**Sonic targets:**
- Genres: ambient electronica, cinematic, new-age, drone
- Tags: `suspended`, `drone`, `ethereal`, `space`, `atmospheric`
- Audio qualities: sparse arrangement, high-frequency shimmer, long sustain, absence of strong pulse
- Avoid: heavy kick drum, strong 4/4 pulse, driving BPM

---

## Selection Rules

1. **Tags are AND-filtered:** a track must match at least one tag from the texture's target list.
   If zero tracks match, fall back to genre filter only.
2. **Avoid-list is a hard exclude:** tracks whose tags include any entry in the `avoid` list are
   removed before ranking (not just deprioritised).
3. **Unknown texture:** if a block's `kinetic_texture` field does not match any key in this map,
   `texture_map.py` raises `ValueError` — do not silently fall back to "no filter".
4. **Composing textures:** a block may declare two textures separated by `+` (e.g., `fluid+grounded`).
   Combine their tag lists with union; intersect their avoid-lists.

---

## Adding New Textures

Add an entry here (with movement quality, sonic targets, avoid list), then add the corresponding
key to `TEXTURE_SONIC_MAP` in `scripts/texture_map.py`. Both files must stay in sync.
