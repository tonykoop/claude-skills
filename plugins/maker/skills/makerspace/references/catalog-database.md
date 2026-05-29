# Catalog database

The skill ships YAML profiles (one folder per space) and Markdown
attachments. That's the source of truth and the human-edit surface.

For *querying* across spaces and projects — "every shop with a
plasma cutter rated for ¼" steel," "every project where the actual
shop time exceeded the estimate by more than 50%," "every CNC job
on baltic birch where measured depth differed from target by more
than 0.005 in" — the YAML is the wrong shape. We promote it into a
SQLite database that the skill can query.

The database is a *read replica*. Don't edit it. Edit the YAML and
markdown, then re-run the build script.

## Schema

The build script (`scripts/build_catalog_db.py`) emits this schema.
Tables and key columns:

### `spaces`
- `slug` (pk), `name`, `city`, `state`, `country`
- `url`, `notebooklm_url`, `visibility`
- `last_updated`, `last_updated_by`

### `tools`
- `id` (pk), `space_slug` (fk → spaces), `name`, `category`
- `location`, `cert_required` (fk → certifications)
- `bed_x_in`, `bed_y_in`, `max_z_in`, `power_w`, `spindle_hp`
  (NULL where N/A)
- `reservation` (`required` | `queue` | `walkup` | NULL)
- One row per tool per space.

### `tool_materials`
- `tool_id` (fk → tools), `material_id` (fk → materials)
- `allowed` (boolean) — denormalized from
  `tools.allowed_materials` / `banned_materials`.

### `materials`
- `id` (pk), `space_slug` (fk), `name`, `category`
- `sheet_x_in`, `sheet_y_in`, `thickness_in`, `typical_cost_usd`
- `available_in_shop` (boolean)

### `certifications`
- `id` (pk), `space_slug` (fk), `name`
- `granted_by_class` (fk → classes)
- `duration_hours`, `cost_usd`

### `classes`
- `id` (pk), `space_slug` (fk), `name`
- `duration_hours`, `cost_usd`, `schedule_url`

### `class_certs`
- `class_id` (fk → classes), `cert_id` (fk → certifications)
  — many-to-many for classes that grant multiple certs.

### `projects`
- `slug` (pk), `space_slug` (fk → spaces, NULL for home shop)
- `name`, `tier` (1, 2, 3)
- `path` (filesystem path to packet)
- `status` (planned | in_progress | shipped | abandoned)
- `created_at`, `shipped_at`

### `project_tools`
- `project_slug` (fk → projects), `tool_id` (fk → tools)
- `op_count` (how many ops cite this tool)

### `measurements`
- `id` (pk autoincrement)
- `project_slug` (fk → projects), `check_id`, `check_name`
- `target`, `tolerance`, `unit`
- `measured`, `delta`, `in_tolerance`
- `measured_at`, `measured_by`, `notes`
- `tool_id` (fk → tools, derived from project's op-sequence)
- `material_id` (fk → materials, derived from cut-list)
- `op_kind` (free-form, e.g., "v-carve", "profile-cut",
  "laser-engrave")
- `dimension_axis` (`x` | `y` | `z` | `depth` | `time` | `cost` |
  `angle` | NULL)

### `corrections`
- `id` (pk autoincrement)
- Composite key (logical): `(space_slug, tool_id, material_id,
  op_kind, dimension_axis)`
- `mean_delta`, `stddev_delta`, `sample_size`
- `last_recomputed_at`
- Recomputed from `measurements` on each `build_catalog_db.py` run.

### `doe_studies`
- `id` (pk), `project_slug` (fk → projects)
- `factor_a_name`, `factor_a_levels` (JSON array)
- `factor_b_name`, `factor_b_levels` (JSON array)
- `replicates`, `response_variable`
- `protocol_path`, `data_path`
- `status` (planned | running | analyzed)

### `doe_runs`
- `id` (pk), `study_id` (fk → doe_studies)
- `factor_a_value`, `factor_b_value`
- `replicate_index`, `response_value`
- `notes`, `recorded_at`

## Building the db

```bash
python3 scripts/build_catalog_db.py \
    --spaces ./spaces/ \
    --projects ./projects/ \
    --output ./catalog.sqlite
```

The script:
1. Walks every `spaces/<slug>/profile.yaml`.
2. Walks every project under `--projects` that contains a
   `design.md` and a `validation.csv`.
3. Walks every `spaces/<slug>/corrections/raw-measurements.jsonl`
   to populate `measurements`.
4. Re-derives `corrections` from `measurements`.
5. Writes the SQLite db.

It's idempotent — run it as often as you want. Default location for
the output is `./catalog.sqlite` at the skill root, ignored by
`.gitignore` so it doesn't get committed.

## Useful queries

```sql
-- Every shop with a plasma cutter rated for ≥ ¼" steel
SELECT space_slug, name FROM tools
WHERE category = 'plasma-cutter';

-- Every project that ran more than 50% over time-budget
SELECT p.slug, m.delta, m.target
FROM measurements m JOIN projects p ON m.project_slug = p.slug
WHERE m.dimension_axis = 'time'
  AND m.delta / m.target > 0.5;

-- Maker Nexus's biggest dimensional bias by tool
SELECT tool_id, op_kind, dimension_axis,
       mean_delta, stddev_delta, sample_size
FROM corrections
WHERE space_slug = 'maker-nexus' AND sample_size >= 5
ORDER BY ABS(mean_delta) DESC
LIMIT 10;

-- Every project that used the laser at any shop
SELECT DISTINCT p.slug, p.name, t.space_slug
FROM project_tools pt
  JOIN tools t ON pt.tool_id = t.id
  JOIN projects p ON pt.project_slug = p.slug
WHERE t.category = 'laser-cutter';
```

## Privacy and visibility

Spaces marked `visibility: private` produce private rows. The
`build_catalog_db.py` script accepts `--public-only` to emit a db
with private spaces excluded — useful for sharing the catalog as a
demo or a benchmarking artifact.

## Why SQLite and not Postgres / DuckDB / a YAML index

- **SQLite** is a single file, runs anywhere Python runs, and the
  query patterns above are well within its sweet spot.
- The catalog will reasonably stay under 100k rows for any single
  user. SQLite handles that without breaking a sweat.
- DuckDB would be better for analytical workloads, but the skill
  doesn't currently need columnar query speed.
- If a real user hits scaling pain, that's a great excuse to swap
  storage — `build_catalog_db.py` is the only seam to change.

## What this isn't

- It isn't a CMS. The YAML stays canonical; the db is read-only.
- It isn't a substitute for `validation.csv` or `measurements.csv`
  in each project. Those stay; the db just rolls them up.
- It isn't a multi-user system. Single-user, single-machine.
- It isn't versioned. Each `build_catalog_db.py` run is a fresh
  derivation. Use git on the YAML/markdown for history.
