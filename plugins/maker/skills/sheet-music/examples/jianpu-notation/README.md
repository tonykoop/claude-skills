# Jianpu output example

Worked example for `scripts/abc_to_jianpu.py` (see
`references/jianpu-notation.md` for the full encoding reference).

`tune.abc` is the same fixture used by
`tests/sample_inputs/tiny-pentatonic.abc` (K:Am, `A B c d e | e d c B A`).
`tune-jianpu.txt` is the generated output, checked in so the shape of the
output is visible without running the script:

```
python ../../scripts/abc_to_jianpu.py --tune tune.abc --out tune-jianpu.txt
```

Note the header renders as `1=C` (Am's relative major) with a note that
the A minor tonic is scale degree `6`, and the dot row above `1 2 3`
marks the lowercase ABC letters (`c d e`) as one octave above the
written register.

This is the base case for the guzheng pilot named in claude-skills
issue #540 -- a real pentatonic guzheng arrangement (typically omitting
scale degrees 4 and 7) would deposit its `tune-jianpu.txt` the same way,
into that instrument's own `learn-to-play/` folder in a follow-up story.
