# Yoga Engine — Shorthand Notation Reference

Version 0.1 · Epic #368 Story #369 · Generic vinyasa vocabulary only.

---

## Overview

The shorthand protocol lets a teacher write a full class plan in a few human-readable lines.
Each line describes one **phase** of the class. A parser expands macros, resolves pose tokens,
and attaches breath operators to produce a structured `Sequence` object.

**Design goals**

- Fast to write on the fly (no special tooling required)
- Human-readable at a glance
- Machine-parseable without ambiguity
- Extensible via custom macros and pose tokens

---

## File structure

```
# META_KEY: value     ← optional meta directives (any order, before/after phases)
LABEL: token_chain    ← one phase per line
```

Blank lines and lines starting with `#` that don't match `# KEY: value` are ignored.

---

## Meta directives

| Directive | Type | Example | Default |
|-----------|------|---------|---------|
| `# TITLE: …` | string | `# TITLE: Sunday Flow` | `Untitled Class` |
| `# DURATION: …` | integer (minutes) | `# DURATION: 60` | `60` |
| `# HEATED: …` | bool (`true`/`false`/`yes`/`no`) | `# HEATED: true` | `false` |
| `# LEVEL: …` | string | `# LEVEL: intermediate` | `mixed` |
| `# THEME: …` | string | `# THEME: hip openers` | _(empty)_ |

Unknown `# KEY: value` lines are silently ignored (forward compatibility).

---

## Phase labels

| Label | Aliases | Phase |
|-------|---------|-------|
| `AR` | `ARR`, `ARRIVAL` | Arrival / centering |
| `WU` | `WARMUP` | Warm-up |
| `BD` | `BLD`, `BUILD` | Build / standing flow |
| `PK` | `PKS`, `PEAK` | Peak pose work |
| `CD` | `CDN`, `COOLDOWN` | Cool-down |
| `SV` | `SAV`, `SAVASANA` | Savasana |

Unknown labels default to `WARMUP` and are preserved as-is in the output.

---

## Pose tokens

Base vocabulary (see `pose_db.py` for full list and safety flags):

| Token | Pose | Family | Intensity |
|-------|------|--------|-----------|
| `SC` | Seated Centering | centering | 1 |
| `BW` | Breath Work | centering | 1 |
| `CB` | Child's Pose | reset | 1 |
| `CC` | Cat-Cow | spinal_mobility | 2 |
| `TB` | Tabletop | warmup | 1 |
| `TNT` | Thread the Needle | twist | 2 |
| `DD` | Downward Dog | transition | 3 |
| `FF` | Forward Fold | forward_fold | 3 |
| `LL` | Low Lunge | hip_opener | 4 |
| `PL` | Plank | transition | 5 |
| `CH` | Chaturanga | transition | 6 |
| `UD` | Upward Dog | backbend | 5 |
| `HL` | High Lunge | standing | 5 |
| `CL` | Crescent Lunge | standing | 5 |
| `WR1` | Warrior I | standing | 6 |
| `WR2` | Warrior II | standing | 6 |
| `WR3` | Warrior III | balance | 7 |
| `TR` | Triangle | standing | 5 |
| `EK` | Extended Side Angle | standing | 5 |
| `RH` | Revolved High Lunge | twist | 6 |
| `RLH` | Revolved Low Lunge | twist | 5 |
| `HP` | Half Moon | balance | 7 |
| `BD` | Bridge | backbend | 5 |
| `PT` | Pigeon | hip_opener | 6 |
| `LZ` | Lizard | hip_opener | 6 |
| `BT` | Bound Angle / Butterfly | hip_opener | 2 |
| `CB2` | Cobra | backbend | 4 |
| `CM` | Camel | backbend | 8 |
| `UB` | Upward Bow / Wheel | backbend | 9 |
| `LB` | Locust | backbend | 5 |
| `CW` | Crow | arm_balance | 8 |
| `SK` | Side Crow | arm_balance | 9 |
| `SH` | Shoulder Stand | inversion | 7 |
| `HH` | Headstand | inversion | 8 |
| `BS` | Boat | core | 6 |
| `ST` | Seated Twist | twist | 3 |
| `SF` | Seated Forward Fold | forward_fold | 3 |
| `SL` | Supine Leg Stretch | cooldown | 2 |
| `KN` | Knees to Chest | reset | 1 |
| `HS` | Happy Baby | hip_opener | 2 |
| `SV` | Savasana | savasana | 1 |

> **Intensity** is 1–10 (1 = deepest rest, 10 = maximum effort peak pose).

---

## Side modifiers

Append `_SIDE` immediately after the token (no space):

| Modifier | Meaning |
|----------|---------|
| `_r` | Right side |
| `_l` | Left side |
| `_f` | Front / forward |
| `_b` | Back / backward |
| `_open` | Open stance |
| `_cl` | Closed stance |

Examples: `WR2_r`, `PT_l`, `EK_open`

---

## Breath counts

Append `/N` after the token (and after any side modifier):

```
DD/5          ← Downward Dog for 5 breaths
PT_r/10       ← Pigeon (right) for 10 breaths
WR2_l/3       ← Warrior II (left) for 3 breaths
```

---

## Breath operators (between poses)

Operators describe how you *enter* the next pose from the previous one:

| Operator | Breath | When to use |
|----------|--------|-------------|
| `+` | Inhale | Rising / opening movement (sweep arms up, step forward) |
| `>` | Exhale | Folding / descending movement (step back, fold forward) |
| `//` | Hold / no breath cue | Transition without a specific breath assignment |

Operator appears **between** pose specs:

```
FF + HL > DD          ← inhale into High Lunge, exhale into Downward Dog
PL > CH + UD > DD     ← chaturanga on exhale, up-dog on inhale, down-dog on exhale
```

If no operator is written before a token, the entry breath is unspecified.

---

## Macros

Macros are named shorthand blocks that expand before parsing.
They can be chained with operators just like regular tokens.

**Built-in macros:**

| Macro | Expands to | Description |
|-------|-----------|-------------|
| `Viny` | `PL>CH+UD>DD` | Full vinyasa |
| `VinyLt` | `PL+UD>DD` | Lighter vinyasa (skip chaturanga) |
| `VinyK` | `PL>CB2+DD` | Cobra vinyasa (beginner-friendly) |
| `VinyC` | `PL>CB2>DD` | Slow cobra vinyasa |
| `HalfA` | `FF+HL>DD` | Half sun-A transition |
| `SunA` | `FF+HL>DD+HL>FF` | Sun Salutation A (abbreviated) |

Macros are expanded in a single pass before pose-token parsing.
Macro names cannot contain other macros (no recursive expansion).

**Custom macros** can be passed to `parse_shorthand(text, macros={...})`.

---

## Chaining: full example

```
# TITLE: Hip-Opening Flow
# DURATION: 60
# LEVEL: mixed
AR: SC/3 > BW/3
WU: CC/5 > TB > DD > LL_r > DD > LL_l
BD: WR2_r > EK_r > Viny > WR2_l > EK_l > Viny > HL_r/3 > Viny > HL_l/3
PK: PT_r/10 > PT_l/10 > CM/5 > CB
CD: ST_r > KN > ST_l > SF/5
SV: SV/5
```

After macro expansion, the `BD` line becomes:

```
BD: WR2_r > EK_r > PL>CH+UD>DD > WR2_l > EK_l > PL>CH+UD>DD > HL_r/3 > PL>CH+UD>DD > HL_l/3
```

---

## Parser API

```python
from yoga_engine import parse_shorthand, validate_sequence, analyze_arc

seq    = parse_shorthand(shorthand_text)
report = validate_sequence(seq)
arc    = analyze_arc(seq)

print(report.is_safe)      # True / False
print(arc.arc_shape)       # "mountain" | "plateau" | ...
print(arc.summary())
```

---

## Validation codes

| Code | Severity | Description |
|------|----------|-------------|
| `PEAK_NO_WARMUP_PHASE` | ERROR | Peak phase present but no warmup/build precedes it |
| `NO_WARMUP_BEFORE_PEAK` | ERROR | A requires-warmup pose in arrival before any warmup |
| `MISSING_COUNTER_AFTER` | ERROR/WARN | Backbend or twist with no counter pose within 3 steps |
| `BILATERAL_MISSING_SIDE` | WARNING | Sided pose missing its mirror |
| `PHASE_ORDER_IRREGULAR` | WARNING | Phases out of expected arc order |
| `INTENSITY_SPIKE` | WARNING | Single-step intensity jump > 3 |
| `SAVASANA_MISSING` | WARNING | No cooldown or savasana phase |
| `HEATED_CAUTION_POSE` | WARNING | Heated-caution pose in a heated class |
| `HEATED_NO_REST_BETWEEN` | WARNING | > 4 consecutive high-intensity poses in heated class |
| `PEAK_TOO_EARLY` | WARNING | High-intensity pose in first 30 % of sequence |

---

## Arc shapes

| Shape | Description |
|-------|-------------|
| `mountain` | Gradual build to a single peak, then tapering descent — ideal |
| `plateau` | Long sustained high-intensity middle section, then drop |
| `spike` | One sharp high-intensity point with low intensity around it |
| `flat` | Little intensity variation throughout |
| `inverted` | Starts and ends high, dips in the middle |
| `wave` | Two or more distinct intensity peaks |
