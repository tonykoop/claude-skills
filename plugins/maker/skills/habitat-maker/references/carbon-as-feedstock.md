# Carbon as Structural Feedstock

**Origin capture:** tonykoop/claude-skills#385 (Move 37 provocation, 2026-06-19)

## Core inversion

Default carbon capture treats sequestered carbon as waste: the win condition is permanent, inert underground storage, and value capture is limited to offset credits. This inverts that. Captured carbon is a feedstock, not a waste stream. Sequestration pays for itself by becoming the raw stock you build the next thing from.

## Material pathways

### 1. CO₂ → Mineralized aggregate (concrete / load-bearing infill)

CO₂ injected into saline water produces carbonic acid → reacts with calcium/magnesium silicates → forms stable calcium carbonate and magnesium carbonate minerals. These can be compressed into aggregate blocks or infill panels. The aggregate is structurally load-bearing and carbon-negative on a lifecycle basis.

**Maker relevance:** carbon-mineralized aggregate for habitat walls, countertops, or cast structural panels. No cement Portland kiln required; the aggregate is self-binding under compression.

### 2. CH₄ → Carbon nanotubes / graphene sheets

Methane cracking (thermal or plasma) splits CH₄ into solid carbon + H₂. The solid carbon fraction can be grown as:
- Multi-wall carbon nanotubes (reinforcing fiber for resin/concrete composite)
- Turbostratic graphene flakes (coating, barrier, or EMI shielding)
- Carbon black (pigment, UV blocker, conductive filler)

**Maker relevance:** nanotube-reinforced resin for instrument bodies, molds, or structural acoustic panels. The H₂ byproduct is clean fuel.

### 3. Mycelium-bound forms from carbon-rich substrate

Mycelium (fungal root network) grown on carbon-rich organic substrate (sawdust, hemp, corn stover) produces rigid, low-density structural composites when dried. Adding captured CO₂ to the growth chamber increases biomass yield and accelerates binding.

**Maker relevance:** mycelium tooling blocks, jigs, and acoustic baffles grown to a specific shape. The form grows itself — no milling, no waste stock. Carbon captured from a nearby process offsets the growth cycle's footprint.

## Economic linkage: WRFCoin Proof-of-Sequestration

Each kilogram of carbon mineralized, cracked, or bound into a structural product is a verifiable sequestration event. This links directly to the WRFCoin Proof-of-Sequestration mechanism: the on-chain attestation records both the sequestration event and the material output, so the instrument or habitat component it produces carries a carbon-negative provenance token.

The supply chain loop: atmospheric CO₂ → structural material → WRFCoin PoS attestation → offset credit + material value → funds the next sequestration run.

## Habitat-maker integration

When designing a habitat build that uses any of these materials, the habitat-maker skill should:

1. Check if the project site has access to a carbon feedstock stream (biogas digester, industrial exhaust, direct air capture unit)
2. Route appropriate fractions to the three material pathways above based on what the build needs (aggregate, reinforcing fiber, or grown form)
3. Flag the PoS linkage to WRFCoin if the builder wants on-chain carbon provenance for the finished structure

## Design table additions

Add to the `bom.csv` for carbon-feedstock builds:

| Material | Source | Carbon pathway | PoS eligible |
|----------|--------|---------------|--------------|
| Carbonate aggregate block | CO₂ mineralization | CO₂ → CaCO₃ | Yes |
| Nanotube resin composite | CH₄ cracking | CH₄ → CNT + H₂ | Yes |
| Mycelium panel | Mycelium growth | CO₂ + organic substrate → biomass | Partial |
