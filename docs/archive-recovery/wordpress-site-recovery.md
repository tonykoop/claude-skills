# tonykoop.com WordPress Site — Content Recovery

Issue: https://github.com/tonykoop/claude-skills/issues/60

## Source

- Capture source: Cowork inventory pass, 2026-05-09.
- Original archive hint: `D:\...\tonykoop.com` (103 MB total)
- Promotion target: feed extracted content into `tonykoop/tonykoop` profile repo

This note defines the content extraction and recovery plan for the archived
WordPress site. It does not copy site files into `claude-skills`.

## What This Is

An archived WordPress portfolio site running the Enfold theme with
LayerSlider for animated hero sections. At ~103 MB, the archive is
predominantly WordPress framework files (~95%); the recoverable content
layer is a small fraction of the total.

Key plugins/themes present in the archive:

| Item | Role |
|---|---|
| Enfold theme | Primary layout/style |
| LayerSlider | Hero/banner slider |
| Akismet | Anti-spam (no content) |
| Bundled wp-themes | Stock themes; no content |

## Content Recovery Target

The only files worth extracting from a WordPress archive are:

### 1. `wp-content/uploads/`
The image library — portfolio photos, project images, icons, any binary
media Tony uploaded. This is the primary recoverable asset. Inspect for:
- Portfolio photography (aerial, instruments, maker projects, apparel)
- Project case study images
- Bio/headshot photos
- Any images that feed the public portfolio

### 2. Post and page content (database export or backup)
If a database export (`.sql`, `.xml`, `.wpress`) exists in the archive,
the post and page content is recoverable by importing or querying it.
Look for:
- Artist bio text
- Project case studies
- Portfolio project descriptions
- Contact/about page copy

Common backup file locations:
```
wp-content/ai1wm-backups/     (All-in-One WP Migration)
wp-content/backup-guard/
*.wpress                       (All-in-One WP export)
*.xml                          (WordPress native export / WXR format)
database-export.sql
db-backup.sql
```

### 3. Theme customization (if any custom CSS/PHP)
If Tony customized Enfold templates or added custom CSS in the theme
editor, those changes live in `wp-content/themes/enfold/` or as a child
theme. Extract only the customized files, not the whole Enfold codebase.

## What to Skip

Everything not in the above three categories is framework boilerplate:

- `wp-admin/` — WordPress admin panel
- `wp-includes/` — WordPress core
- `wp-content/plugins/` — third-party plugins (akismet, etc.)
- `wp-content/themes/` — stock themes (only extract Tony's customizations)
- `wp-config.php` — **never commit** (contains database credentials)
- `.htaccess` — server config, not content

## Extraction Steps

1. Stage `D:\...\tonykoop.com\` locally (or mount the archive).
2. **Immediately exclude sensitive files** before any inspection:
   - `wp-config.php` (database credentials)
   - Any `.env` files
   - Log files with IP addresses (`access.log`, `error.log`)
3. Inventory `wp-content/uploads/`:
   ```bash
   find wp-content/uploads -type f | \
     awk -F. '{print $NF}' | sort | uniq -c | sort -rn
   ```
   Generate a file-type summary to understand what's there.
4. Search for database exports:
   ```bash
   find . -name "*.sql" -o -name "*.wpress" -o -name "*.xml" | head -20
   ```
5. If a WXR export (`.xml`) is found, parse it for post/page titles and
   content. WordPress WXR is standard XML and can be queried with `xmllint`
   or a basic Python parser.
6. Extract `wp-content/uploads/` into a staging folder; organize by year
   (WordPress stores uploads in `uploads/YYYY/MM/`).
7. Draft recovered text content (bio, project descriptions) into Markdown.

## Proposed Output in `tonykoop/tonykoop` Profile Repo

```text
tonykoop/
  README.md
  portfolio/
    images/
      (uploads extracted from WordPress)
    projects/
      aerial-photography.md
      instruments.md
      maker-projects.md
      apparel.md
  bio/
    artist-bio.md
    contact.md
  archive/
    wordpress-recovery-log.md
    content-inventory.md
```

## Owner Decisions Required

1. **Is there a database export in the archive?** If no `.sql` / `.wpress` /
   `.xml` backup exists, post/page text is not recoverable without the live
   database.
2. **What images are in `wp-content/uploads/`?** These may overlap with
   the aerial photography (#44), instrument repos (#92, #100), and apparel
   (#54, #56) archives. Cross-reference during inventory.
3. **Custom theme work**: did Tony write custom CSS or page templates? If
   yes, extract the customizations; if the site was stock Enfold, skip.
4. **tonykoop.com domain**: is the domain still registered and pointing
   somewhere? If the site is still live, content can be scraped more
   easily than from the archive.

## Related Work

- `docs/archive-recovery/aerial-photography-recovery.md` (#44) — portfolio
  images from the uploads directory may overlap with aerial folders.
- Issues #92 and #100 (image-gen-2 for instrument repos) — any instrument
  portfolio images from the WordPress uploads would feed those.
- `tonykoop/tonykoop` profile repo — the promotion target; current README
  state determines how recovered content integrates.

## Review Notes

- Do not guess at post content. Extract from the database export or from
  `wp-content/uploads/` filenames only — do not fabricate bio text.
- The Enfold theme LayerSlider content (slider images, captions) may be
  stored in the database, not in flat files — recoverable only if a DB
  export exists.
- `wp-config.php` must never be committed anywhere. If present in staging,
  delete it before any `git add`.
