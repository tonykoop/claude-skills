#!/usr/bin/env python3
"""Aggregate grading + timing into a benchmark.json suitable for the
eval viewer."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: aggregate_benchmark.py <iteration-dir>")
        return 2
    iter_dir = Path(argv[1]).resolve()

    eval_dirs = sorted(
        [d for d in iter_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
    )

    benchmark = {
        "iteration": iter_dir.name,
        "skill_name": "makerspace",
        "evals": [],
        "configurations": {
            "with_skill": {
                "pass_rates": [],
                "durations_seconds": [],
                "total_tokens_list": [],
            },
            "without_skill": {
                "pass_rates": [],
                "durations_seconds": [],
                "total_tokens_list": [],
            },
        },
    }

    for eval_dir in eval_dirs:
        eval_entry = {"name": eval_dir.name, "runs": {}}
        meta_path = eval_dir / "eval_metadata.json"
        if meta_path.exists():
            eval_entry["prompt"] = json.loads(meta_path.read_text()).get("prompt", "")
        for variant in ["with_skill", "without_skill"]:
            variant_dir = eval_dir / variant
            if not variant_dir.exists():
                continue
            grading_path = variant_dir / "grading.json"
            timing_path = variant_dir / "timing.json"
            run = {}
            if grading_path.exists():
                grading = json.loads(grading_path.read_text())
                run["grading"] = grading
                pass_rate = (
                    grading["passed_count"] / grading["total_count"]
                    if grading["total_count"] > 0 else 0.0
                )
                run["pass_rate"] = pass_rate
                benchmark["configurations"][variant]["pass_rates"].append(pass_rate)
            if timing_path.exists():
                timing = json.loads(timing_path.read_text())
                run["timing"] = timing
                if "total_duration_seconds" in timing:
                    benchmark["configurations"][variant]["durations_seconds"].append(
                        timing["total_duration_seconds"]
                    )
                if "total_tokens" in timing:
                    benchmark["configurations"][variant]["total_tokens_list"].append(
                        timing["total_tokens"]
                    )
            eval_entry["runs"][variant] = run
        benchmark["evals"].append(eval_entry)

    # Compute aggregates
    def mean(xs): return sum(xs) / len(xs) if xs else 0.0
    def stddev(xs):
        if len(xs) < 2:
            return 0.0
        m = mean(xs)
        return (sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5

    for variant in ["with_skill", "without_skill"]:
        cfg = benchmark["configurations"][variant]
        cfg["pass_rate_mean"] = round(mean(cfg["pass_rates"]), 3)
        cfg["pass_rate_stddev"] = round(stddev(cfg["pass_rates"]), 3)
        cfg["duration_mean_seconds"] = round(mean(cfg["durations_seconds"]), 1)
        cfg["duration_stddev_seconds"] = round(stddev(cfg["durations_seconds"]), 1)
        cfg["tokens_mean"] = int(mean(cfg["total_tokens_list"]))
        cfg["tokens_stddev"] = int(stddev(cfg["total_tokens_list"]))

    # Delta
    ws = benchmark["configurations"]["with_skill"]
    nos = benchmark["configurations"]["without_skill"]
    benchmark["delta"] = {
        "pass_rate_delta": round(ws["pass_rate_mean"] - nos["pass_rate_mean"], 3),
        "duration_delta_seconds": round(ws["duration_mean_seconds"] - nos["duration_mean_seconds"], 1),
        "tokens_delta": ws["tokens_mean"] - nos["tokens_mean"],
    }

    out_path = iter_dir / "benchmark.json"
    out_path.write_text(json.dumps(benchmark, indent=2))
    print(f"Wrote {out_path}")
    print()
    print(f"With skill:    pass {ws['pass_rate_mean']:.0%} ± {ws['pass_rate_stddev']:.0%}, "
          f"duration {ws['duration_mean_seconds']:.0f}s, tokens {ws['tokens_mean']:,}")
    print(f"Without skill: pass {nos['pass_rate_mean']:.0%} ± {nos['pass_rate_stddev']:.0%}, "
          f"duration {nos['duration_mean_seconds']:.0f}s, tokens {nos['tokens_mean']:,}")
    print(f"Delta:         pass {benchmark['delta']['pass_rate_delta']:+.0%}, "
          f"duration {benchmark['delta']['duration_delta_seconds']:+.0f}s, "
          f"tokens {benchmark['delta']['tokens_delta']:+,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
