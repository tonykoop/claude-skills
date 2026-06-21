# Structural Polish Pass — Reference

The structural-polish pass examines the script's narrative architecture: does it hook the viewer in the first 5 seconds, sustain momentum through the body, and close with a landing that converts? This is the narrative equivalent of a story editor pass in Hollywood development.

## Goals

1. Score the hook strength so the director knows whether the opening works.
2. Flag on-the-nose lines that rob the image of its meaning.
3. Identify retention-curve drag points where viewer attention will drop.
4. Audit transitions for rhythm and earned movement.
5. Score the closing strength and check CTA clarity.

## Procedure

### 1. Hook strength rating (0–10)

Evaluate the first 5 seconds (approximately the first 15–25 words of spoken content):

| Score | Meaning |
|-------|---------|
| 9–10 | Viewer is instantly oriented AND emotionally engaged; wants to see the next frame |
| 7–8 | Strong — clear setup with a mild pull forward |
| 5–6 | Serviceable — viewer stays but isn't hooked; will skim or tab away on mobile |
| 3–4 | Weak — slow, generic, or self-referential ("Hi, welcome to my channel…") |
| 1–2 | Dead — viewer actively exits; no reason to stay |

Criteria:
- **Immediate payoff**: first sentence delivers a specific, concrete thing (a question, a surprising image, a bold claim)
- **Pattern interruption**: something unexpected in word choice, rhythm, or concept
- **Specificity**: generic statements score lower regardless of energy level

### 2. On-the-nose line detection

A line is **on-the-nose** when it tells the viewer what to feel instead of showing the thing that would cause the feeling.

Examples:
| On-the-nose | Visual-forward alternative |
|-------------|---------------------------|
| "This is a really empowering class." | "By the last pose, you'll stand differently." |
| "We care deeply about the environment." | Cut to the close-up of hands in soil — no narration needed |
| "This instrument is beautiful." | Hold on the instrument for 2 seconds; let the image do it |

Flag every on-the-nose line. For each, suggest either:
- A rewrite that shows rather than tells, OR
- A `[VISUAL HOLD]` instruction (drop the line; let B-roll carry the moment)

### 3. Retention-curve drag points

Mark any segment longer than 8 seconds of A-roll narration without a visual pivot, tonal change, or new information. These are drag points where algorithmic re-engagement signals typically drop.

Rate each drag point:
- **BLOCKER**: > 15 seconds of undifferentiated content; must restructure
- **POLISH**: 8–15 seconds; add a visual cut or rhythm shift

### 4. Transition audit

For each scene or section transition, assess:

| Transition type | When it works | When it fails |
|----------------|--------------|---------------|
| **Cold cut** | High energy, topic shift, momentum | Feels jarring when mood is contemplative |
| **Dissolve / cross-fade** | Emotional continuity, time passage | Signals indecision when overused |
| **Audio bridge** | Rhythmic continuity; sound before image | Works in yoga / reflective arcs |
| **Title card** | Chapter structure, instructional content | Kills momentum in narrative formats |
| **J-cut / L-cut** | Anticipation, memory, continuity | Hard to execute in scripted VO — note only when scripted |

Flag transitions that don't match the channel archetype or narrative intent.

### 5. Closing strength rating (0–10)

Evaluate the final 5 seconds:

| Score | Meaning |
|-------|---------|
| 9–10 | Clean landing with earned emotional beat AND clear CTA |
| 7–8 | Good — strong one or the other |
| 5–6 | Soft — ending trails off or CTA feels bolted on |
| 1–4 | Abrupt / missing — video just stops |

Check CTA clarity:
- Is there exactly ONE action asked of the viewer?
- Is it stated once, simply?
- Does it match the channel archetype? (yoga → "continue your practice"; maker → "build this with me"; AI → "subscribe for the next build")

## Output format

Produce a `## Structural Polish Pass` section in the review document with:

1. **Hook strength: N/10** — one-paragraph rationale
2. **On-the-nose lines** — bulleted list (offending line → suggested fix or `[VISUAL HOLD]`)
3. **Retention drag points** — table (TC-in, TC-out, type, fix)
4. **Transition audit** — flagged transitions with type and recommendation
5. **Closing strength: N/10** — rationale + CTA clarity verdict (CLEAR / UNCLEAR / MISSING)

If no issues are found in a section, write: `None found.`
