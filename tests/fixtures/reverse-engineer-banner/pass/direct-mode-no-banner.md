# Example: Reverse-engineer notes with direct image access

```yaml
intake:
  image_access_mode: direct
  images_referenced: 3
  images_viewable: 3
  recovery_path: not-needed
  source_qualifiers: []
  confidence_ceiling: full
  notes: ""
```

When `image_access_mode` is `direct`, no degraded-mode banner is required. This fixture exists to confirm the validator does not falsely flag direct-mode outputs.
