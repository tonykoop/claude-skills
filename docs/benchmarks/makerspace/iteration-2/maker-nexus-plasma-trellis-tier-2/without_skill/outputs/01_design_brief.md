# 01 - Design Brief

## Intent

A 6-foot freestanding garden trellis whose silhouette evokes a climbing vine: trunk-like central spine with curling tendrils and three sizes of leaves (small at top, large at base, mirrored across a vertical axis to suggest growth). The cut steel itself is the trellis - climbing plants weave through openings between leaves and tendrils.

## Overall dimensions

- Height: 72.0" overall (66.0" exposed + 6.0" ground stake)
- Width: 24.0" maximum (mid-panel, where the largest leaves project)
- Width at base spine: 4.0"
- Thickness: 0.250" (single plate, no laminations)
- Estimated cut weight: ~28 lb after voids removed (from ~40 lb starting blank)

## Pattern logic

- **Central spine**: continuous, 1.5" minimum width anywhere along its length. Structural backbone; rule of thumb is "no neck thinner than 6x material thickness in tension" - 1.5" = 6 x 0.25".
- **Leaves**: 3 sizes - 6" (x4), 4" (x6), 2.5" (x8). Each has an interior negative-space vein (slot, ~0.25" x 1.5"). Veins are **internal cuts** - require a pierce in the middle of material; flagged in cut strategy.
- **Tendrils**: spiral curls, 0.5" minimum stroke width. Two tendrils have closed loops (through-holes) for tying in plant ties.
- **No sharp inside corners**: every concave corner has a fillet >= 0.25". Plasma cannot faithfully reproduce sharper inside corners and they become stress risers under wind load.

## Structural rationale (wind-load sanity check)

A 72" cantilevered steel plate in 1/4" mild experiences modest moment load even with a 50 mph gust against the projected area.

- Projected face area (silhouette outline): ~1.4 sq ft
- Wind pressure at 50 mph (drag coeff 1.2 for irregular shape): ~10 psf
- Force: ~14 lbf at centroid (~30" up from base)
- Moment at ground: ~420 lbf-in
- Section modulus of 4" x 0.25" plate (weak axis): S = b h^2 / 6 = 4 (0.25^2) / 6 = 0.042 in^3
- Stress: 420 / 0.042 ~ 10,000 psi vs A36 yield 36,000 psi

Margin ~3.6x. Adequate for residential garden use. NOT modeled for trained roses or wisteria with significant crown weight.

## Aesthetic constraints

- All leaf and tendril curves are CONTINUOUS (no kinks) - drawn as Bezier splines.
- Outer silhouette is one closed path; internal voids are separate closed paths.
- Mirrored about the vertical centerline so the cut is symmetric (helps cut path balance and visual weight).
