"""
archive_recovery.cli_demo
=========================
End-to-end demonstration of the archive-recovery pipeline.

Runs entirely offline — no network, no filesystem reads, no randomness.
Simulates recovering a realistic maker archive containing:
  - Stencil projects (CAD: .step, .dxf)
  - Chessboard table (CAD: .f3d, photos: .jpg, docs: .pdf)
  - Custom instrument neck (CAD: .step, .stl, code: .py)
  - Sewing/apparel (docs: .pdf, photos: .jpg)
  - Aerial/drone electronics (code: .ino, .py, CAD: .gerber)
  - Media footage (media: .mp4, .mov)

Plus: 3 exact duplicates, 2 near-dups, 1 stale pair, 1 large binary (>100 MB).

Entry point: python3 -m archive_recovery.cli_demo
Returns a dict for testability via run_demo().
"""

from __future__ import annotations

from .models import FileRecord
from .workflow import RecoveryWorkflow
from .manifest import build_manifest, RepoManifest
from .migration import plan_migration
from .scaffold import plan_scaffold


# ---------------------------------------------------------------------------
# Fixed fake content hashes
# ---------------------------------------------------------------------------

_DUP_HASH = "aabbcc112233ddeeff4455667788990011223344556677889900aabbccddeeff"


def _build_records() -> list[FileRecord]:
    """
    Build 27 deterministic FileRecord objects covering 6 project types.

    Path convention: <project_name>/... so the classifier picks the first
    directory component as the project name.  The "_archive_" middle segment is
    omitted so multiple distinct project groups are produced.

    Includes:
      - 3 records with identical content_hash (exact duplicates)
      - 2 records with the same filename in different directories and sizes
        within 5% of each other (near-dups: process_01.jpg)
      - 2 records with the same stem+extension but different mtime (stale pair:
        laser_template.dxf at v1 vs v2)
      - 1 record with size_bytes > 100 MB (large binary LFS candidate)
    """
    return [
        # ------------------------------------------------------------------
        # 1. Stencil project — CAD files
        # ------------------------------------------------------------------
        FileRecord(
            path="stencils/v2/laser_template.dxf",
            mtime=1_715_000_000.0,
            size_bytes=48_200,
        ),
        FileRecord(
            path="stencils/v2/mounting_bracket.step",
            mtime=1_715_010_000.0,
            size_bytes=125_400,
        ),
        # Stale pair: same stem+extension, older mtime
        FileRecord(
            path="stencils/v1/laser_template.dxf",
            mtime=1_714_900_000.0,
            size_bytes=46_800,
        ),

        # ------------------------------------------------------------------
        # 2. Chessboard table — CAD, photos, docs
        # ------------------------------------------------------------------
        FileRecord(
            path="chessboard_table/cad/table_top.f3d",
            mtime=1_715_100_000.0,
            size_bytes=320_000,
        ),
        FileRecord(
            path="chessboard_table/cad/leg_assembly.step",
            mtime=1_715_110_000.0,
            size_bytes=210_000,
        ),
        FileRecord(
            path="chessboard_table/photos/finished_top.jpg",
            mtime=1_715_120_000.0,
            size_bytes=3_800_000,
        ),
        # Near-dup pair: same filename "process_01.jpg" in two dirs, size within 5%
        FileRecord(
            path="chessboard_table/photos/process_01.jpg",
            mtime=1_715_125_000.0,
            size_bytes=2_900_000,
        ),
        FileRecord(
            path="chessboard_table/photos_alt/process_01.jpg",
            mtime=1_715_126_000.0,
            size_bytes=2_987_000,  # ~2.9% larger → within 5% tolerance
        ),
        FileRecord(
            path="chessboard_table/docs/design_brief.pdf",
            mtime=1_715_130_000.0,
            size_bytes=95_000,
        ),

        # ------------------------------------------------------------------
        # 3. Custom instrument neck — CAD, code
        # ------------------------------------------------------------------
        FileRecord(
            path="instrument_neck/cad/neck_profile.step",
            mtime=1_715_200_000.0,
            size_bytes=480_000,
        ),
        FileRecord(
            path="instrument_neck/cad/fret_slots.stl",
            mtime=1_715_210_000.0,
            size_bytes=260_000,
        ),
        FileRecord(
            path="instrument_neck/code/fret_calc.py",
            mtime=1_715_220_000.0,
            size_bytes=12_000,
        ),
        FileRecord(
            path="instrument_neck/code/string_tension.py",
            mtime=1_715_225_000.0,
            size_bytes=8_400,
        ),

        # ------------------------------------------------------------------
        # 4. Sewing / apparel — docs, photos
        # ------------------------------------------------------------------
        FileRecord(
            path="sewing_apparel/docs/pattern_v3.pdf",
            mtime=1_715_300_000.0,
            size_bytes=430_000,
        ),
        FileRecord(
            path="sewing_apparel/docs/sizing_chart.pdf",
            mtime=1_715_305_000.0,
            size_bytes=87_000,
        ),
        FileRecord(
            path="sewing_apparel/photos/mock_up_front.jpg",
            mtime=1_715_310_000.0,
            size_bytes=4_200_000,
        ),
        FileRecord(
            path="sewing_apparel/photos/mock_up_back.jpg",
            mtime=1_715_315_000.0,
            size_bytes=3_950_000,
        ),

        # ------------------------------------------------------------------
        # 5. Aerial / drone electronics — code, CAD
        # ------------------------------------------------------------------
        FileRecord(
            path="aerial_drone/firmware/flight_ctrl.ino",
            mtime=1_715_400_000.0,
            size_bytes=34_000,
        ),
        FileRecord(
            path="aerial_drone/firmware/telemetry.py",
            mtime=1_715_410_000.0,
            size_bytes=18_500,
        ),
        FileRecord(
            path="aerial_drone/pcb/motor_driver.gerber",
            mtime=1_715_420_000.0,
            size_bytes=62_000,
        ),

        # ------------------------------------------------------------------
        # 6. Media footage
        # ------------------------------------------------------------------
        FileRecord(
            path="media_footage/build_timelapse.mp4",
            mtime=1_715_500_000.0,
            size_bytes=120_000_000,   # >100 MB — large binary / LFS candidate
        ),
        FileRecord(
            path="media_footage/final_reveal.mov",
            mtime=1_715_510_000.0,
            size_bytes=45_000_000,
        ),

        # ------------------------------------------------------------------
        # Exact duplicates — 3 records sharing the same content_hash
        # (classifier places them in "stencils" project group since they
        # share the stencils/ top-level dir)
        # ------------------------------------------------------------------
        FileRecord(
            path="stencils/exports/laser_template_export.dxf",
            mtime=1_715_020_000.0,
            size_bytes=48_200,
            content_hash=_DUP_HASH,
        ),
        FileRecord(
            path="stencils/backup/laser_template_bak.dxf",
            mtime=1_715_030_000.0,
            size_bytes=48_200,
            content_hash=_DUP_HASH,
        ),
        FileRecord(
            path="stencils/final/laser_template_final.dxf",
            mtime=1_715_040_000.0,
            size_bytes=48_200,
            content_hash=_DUP_HASH,
        ),

        # ------------------------------------------------------------------
        # Additional stencil photo to round out the stencils group
        # ------------------------------------------------------------------
        FileRecord(
            path="stencils/photos/result_photo.jpg",
            mtime=1_715_050_000.0,
            size_bytes=2_200_000,
        ),
    ]


def run_demo() -> dict:
    """
    Execute the full archive-recovery pipeline on a synthetic maker archive.

    Returns
    -------
    dict
        Summary keys: total_files, project_count, duplicate_count,
        workflow_stage, first_project, migration_adds, migration_skips.
    """
    records = _build_records()

    # ------------------------------------------------------------------
    # 1. Ingest + run full pipeline
    # ------------------------------------------------------------------
    wf = RecoveryWorkflow()
    wf.ingest(records)
    wf.run()

    # ------------------------------------------------------------------
    # 2. Build the top-level RecoveryManifest and print its summary
    # ------------------------------------------------------------------
    manifest = wf.build_manifest()
    summary = manifest.export_dict()

    print("=== RecoveryManifest summary ===")
    for key, value in summary.items():
        if key not in ("projects", "dedup_report"):
            print(f"  {key}: {value}")
    print(f"  projects ({summary['project_count']} groups):")
    for pg in summary["projects"]:
        print(f"    {pg['project']!r}: {pg['item_count']} items")

    # ------------------------------------------------------------------
    # 3. Per-project scaffold + repo manifest for the first project group
    # ------------------------------------------------------------------
    first_group = manifest.projects[0]
    first_project_name = first_group.project
    first_items = first_group.items

    plan = plan_scaffold(first_project_name, first_items)
    repo_manifest: RepoManifest = build_manifest(plan, first_items)

    print()
    print(repo_manifest.to_text_summary())

    # ------------------------------------------------------------------
    # 4. Simulate an existing repo tree and plan migration
    # ------------------------------------------------------------------
    # Pick the first dest_path from the repo manifest (to produce a SKIP)
    # and invent an extra orphan file (to produce a REMOVE).
    existing_tree: dict[str, str] = {}

    # If the manifest has at least one entry, add it to existing_tree
    # with its real hash → should produce a SKIP.
    for section in repo_manifest.sections:
        for entry in section.entries:
            existing_tree[entry.dest_path] = entry.content_hash
            break   # only one entry → rest will be ADDs
        break

    # Orphan — present in repo but absent from manifest → REMOVE.
    existing_tree["misc/orphan_old_file.txt"] = "deadbeef00112233"

    migration_plan = plan_migration(repo_manifest, existing_tree)

    print()
    print("=== MigrationPlan ===")
    for line in migration_plan.summary_lines():
        print(f"  {line}")

    # ------------------------------------------------------------------
    # 5. Workflow summary
    # ------------------------------------------------------------------
    print()
    print("=== Workflow summary ===")
    for line in wf.summary_lines():
        print(f"  {line}")

    return {
        "total_files": len(records),
        "project_count": manifest.project_count,
        "duplicate_count": manifest.duplicate_count,
        "workflow_stage": wf.stage.value,
        "first_project": first_project_name,
        "migration_adds": len(migration_plan.adds),
        "migration_skips": len(migration_plan.skips),
    }


if __name__ == "__main__":
    run_demo()
