# Jig Decision Matrix

Use this matrix when deciding whether to make, adapt, buy, order, or
borrow a jig or fixture.

| Condition | Prefer make | Prefer adapt existing | Prefer buy/order | Prefer borrow |
| --- | --- | --- | --- | --- |
| One-off part, loose tolerance | Rarely | Often | Rarely | Sometimes |
| Small batch, moderate repeatability | Often | Often | Sometimes | Sometimes |
| Recurring job, stable geometry | Often | Sometimes | Often | Rarely |
| Tight tolerance / high rigidity | Often | Sometimes | Often if known-good | Rarely |
| Urgent deadline | Sometimes | Often | Often if in stock | Often |
| Unknown geometry still changing | Avoid overbuilding | Best first move | Avoid custom order | Good short-term choice |

## Evaluation factors

Score each candidate on:

- Accuracy and stiffness
- Setup time per part
- Time to first good part
- Reuse frequency
- Cost of materials and hardware
- Lead time
- Safety and operator error resistance
- Ease of inspection

## Common patterns

- **Dedicated drill jig**
  Good for repeated hole locations where setup time dominates.
- **Modular T-track or fixture-plate setup**
  Good when geometry changes but datum strategy stays similar.
- **Sacrificial carrier or onion-skin fixture**
  Good for small laser or CNC parts that want to shift after contouring.
- **Soft jaws**
  Good for low-volume precision clamping on mills and lathes.
- **Commercial template or guide bushing kit**
  Good when the feature is generic and time matters more than custom fit.

## Red flags

- Recommending a "custom jig" without naming datums, stops, or clamping
- Spending more time building the jig than the batch justifies without a
  reuse plan
- Choosing the highest-precision option when the real failure mode is poor
  inspection discipline
