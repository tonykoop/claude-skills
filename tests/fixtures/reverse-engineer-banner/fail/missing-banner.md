# Example: degraded intake but the banner was forgotten

```yaml
intake:
  image_access_mode: description-only
  images_referenced: 1
  images_viewable: 0
  recovery_path: requested-and-declined
  source_qualifiers: [user-prose]
  confidence_ceiling: provisional
  notes: ""
```

This fixture is intentionally broken: `image_access_mode` is `description-only`, but the standardized degraded-mode banner is missing from the top of the artifact. The validator should reject it.
