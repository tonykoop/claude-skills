# Shorthand Protocol

Use this reference when the user asks to write, inspect, or debug Tony-style yoga shorthand. The protocol is intentionally small enough to author by hand during class planning.

## Token Table

### Starter Poses

| Token | Pose | Notes |
|---|---|---|
| `DD` | Downward Facing Dog | reset, transition, or breath hold |
| `HL` | Half Lift | inhale lift from forward fold |
| `FF` | Standing Forward Fold | fold, ragdoll, or reset |
| `RLH` | Runner's Lunge | side-sensitive lunge entry |
| `CL` | Crescent Lunge | standing lunge target |
| `PT` | Prayer Twist | side-sensitive twist; treat as constraint-sensitive |

`PL`, `CH`, and `UD` are included in `pose_thesaurus.json` as macro-support tokens because the starter `Viny` block expands through them.

### Modifiers

| Modifier | Meaning |
|---|---|
| `_r` | right side |
| `_l` | left side |
| `_f` | facing front |
| `_b` | facing back |
| `_open` | open hip or open twist orientation |
| `_cl` | closed hip or closed twist orientation |

Attach modifiers directly to pose tokens: `RLH_r`, `CL_l`, `PT_open`.

### Breath And Pacing Operators

| Operator | Meaning |
|---|---|
| `+` | inhale into the next shape |
| `>` | exhale or transition into the next shape |
| `//` | hold in place |
| `5B` | hold for five breaths; any positive integer followed by `B` is valid |

Operators can be written with or without spaces: `FF>HL+FF` and `FF > HL + FF` are equivalent.

## Macro Blocks

Define one macro per line with `Name = expression`. Macro names start with a capital letter and can contain letters or numbers.

```text
Viny = PL>CH+UD>DD
```

The packaged `Viny` macro expands to:

```text
PL > CH + UD > DD
```

Use macros as phrases inside later lines:

```text
FF > HL + FF > Viny
```

## Five-Line Starter Class

This sample is deliberately compact and human-authorable:

```text
Viny = PL>CH+UD>DD
DD // 5B
RLH_r > CL_r // 5B > PT_r
RLH_l > CL_l // 5B > PT_l
FF > HL + FF > Viny
```

Run it through the public loader with:

```bash
python3 plugins/maker/skills/yoga-sequencer/scripts/engine_config.py --program-file /path/to/shorthand.txt --json
```

The parser must consume every non-whitespace character. If a line contains unknown punctuation or malformed syntax, it should fail loudly instead of guessing.
