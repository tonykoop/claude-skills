# Constraint-Injection Prompt - Universal Design Guide compatibility

Story #246 of the Cross-Pollination Engine (epic #236). This is a reusable
**prompt fragment** that injects the Universal Interface guide (#245)
constraints into any design-generation request, so generated designs default to
the standard interfaces instead of inventing new ones.

Paste the fragment ahead of (or around) any "design me a ..." request to an LLM
or a downstream design skill (`maker-engineering`, `makerspace`,
`instrument-maker`).

## The prompt fragment (copy-paste)

```text
DESIGN CONSTRAINTS - Universal Interface Guide (the "Lego rule").
The design you produce MUST be swappable with other subassemblies in this
portfolio. Before proposing geometry, satisfy ALL of the following and state
the tokens you chose:

1. MOUNTING: expose at least one standard mount face. Choose from:
   t-slot-2020 (M5), t-slot-3030 (M6), vesa-75 (M4), vesa-100 (M4),
   hole-pattern-43x43 (M4), dovetail-arca, keyhole-pair. A bespoke face is
   allowed ONLY in addition to one standard face.
2. FASTENERS: use M5 for structure and M3 for electronics by default. In
   printed plastic, specify heat-set inserts (heat-set-m3 / heat-set-m5), never
   tapped plastic. Imperial (1/4-20) only for legacy camera/photo interfaces;
   if used, justify it.
3. FITS: name every mating fit as one of clearance-loose, slip-h7, press-p7,
   or thread. Default FDM mating parts to clearance-loose plus a test coupon.
4. ELECTRICAL (if any): use connector tokens xt60 (keyed DC power),
   jst-ph (signal), usb-c (user-facing), or grove (prototyping); declare a
   single VCC (3v3 or 5v); use pinout i2c-4pin or uart-3v3 with documented pin
   order. No bare-wire DC.
5. NAMING: name the subassembly <domain>-<function>-<variant>, e.g.
   maker-index-detent-8mm.
6. OUTPUT: end with an `interfaces:` YAML list (mount:, fastener:, tolerance:,
   connector:, pinout: as applicable) ready to paste into the idea frontmatter.

If a constraint genuinely cannot be met, say so explicitly and propose the
smallest deviation rather than silently inventing a non-standard interface.
```

## Usage notes

- **Where to inject:** prepend the fragment to the user's design request. For
  long agent prompts, place it in the system / developer message so it survives
  the whole session.
- **Keep it in sync:** the token lists above are a mirror of
  [`universal-interface-guide.md`](../universal-interface-guide.md) (#245). If
  that guide changes, update this fragment in the same PR.
- **Pair with tagging:** the fragment's step 6 emits an `interfaces:` block in
  the exact shape the functional-tagging schema (#243) expects, so a generated
  design is immediately taggable and therefore cross-pollinatable (#247).
- **Portable phrasing:** the fragment is plain text with no client-specific
  syntax, so it works in Claude, Codex, and Gemini CLI alike.
- **Escalation:** the last line is deliberate - a model that cannot meet a
  constraint should surface the deviation, not hide it. Reviewers can then catch
  a drifting interface before it ships.

## Before / after example

**Request:** "Design a quick-release bracket to hold a small camera on my
instrument stand."

### Before (no constraint injection)

> Here's a bracket: a 3D-printed L-plate with two M4 holes spaced 30 mm apart
> to bolt onto the stand, and a 1/4" screw to hold the camera. Glue a captive
> nut in the back.

Problems: invented 30 mm hole spacing (matches nothing else in the portfolio),
tapped/glued plastic instead of a heat-set insert, no named fit, no
`interfaces:` block, not reusable.

### After (with constraint injection)

> Chosen tokens: `mount:dovetail-arca` (camera side), `mount:t-slot-2020`
> (stand side), `fastener:1/4-20` (camera, legacy interface - justified:
> standard tripod thread), `fastener:m5` + `fastener:heat-set-m5` (stand side),
> `tolerance:clearance-loose` (printed dovetail).
>
> Design: an Arca-Swiss dovetail clamp for the camera, on a body that bolts to
> the stand via a single T-slot-2020 face using M5 screws into heat-set
> inserts. Print a clearance-loose test coupon for the dovetail first.
>
> ```yaml
> interfaces:
>   - mount:dovetail-arca
>   - mount:t-slot-2020
>   - fastener:1/4-20
>   - fastener:heat-set-m5
>   - tolerance:clearance-loose
> ```

The "after" bracket now mates with every other T-slot-2020 module and every
Arca-Swiss plate in the portfolio, and it arrives pre-tagged for the MOC (#244)
and the agent (#247).
