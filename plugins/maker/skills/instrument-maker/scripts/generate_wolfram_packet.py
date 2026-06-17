#!/usr/bin/env python3
"""
Generate a richer Wolfram Language source package for a build packet.

The output is readable `.wl` source that can be opened directly in Wolfram
Desktop/Cloud. If `wolframscript` is available and --execute is passed, the
script asks Wolfram to evaluate the source and create a notebook.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import subprocess
from datetime import date
from pathlib import Path
from typing import Iterable


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def wl_string(value: object) -> str:
    text = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{text}"'


def assoc(items: dict[str, object], indent: str = "  ") -> str:
    pairs = []
    for key, value in items.items():
        if isinstance(value, (int, float)):
            rendered = str(value)
        else:
            rendered = wl_string(value)
        pairs.append(f"{indent}{wl_string(key)} -> {rendered}")
    return "<|\n" + ",\n".join(pairs) + "\n|>"


def parse_title(text: str) -> str:
    match = re.search(r"^#\s+(.+)$", text, re.M)
    return match.group(1).strip() if match else "Instrument Packet"


def extract_model(text: str) -> str:
    lower = text.lower()
    if "helmholtz" in lower:
        return "Helmholtz"
    if "stopped pipe" in lower or "stopped-pipe" in lower:
        return "StoppedPipe"
    if "open pipe" in lower or "open-pipe" in lower:
        return "OpenPipe"
    if "cantilever" in lower:
        return "CantileverBeam"
    if "free-free" in lower or "free free" in lower:
        return "FreeFreeBeam"
    if "mersenne" in lower or "string" in lower:
        return "String"
    return "Generic"


def sample_csv(path: Path, limit: int = 8) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return [row for _, row in zip(range(limit), reader)]


def metadata(packet: Path) -> dict[str, object]:
    design = read_text(packet / "design.md")
    readme = read_text(packet / "README.md")
    combined = f"{design}\n{readme}"
    return {
        "PacketName": parse_title(combined),
        "PacketPath": str(packet),
        "GeneratedOn": date.today().isoformat(),
        "Model": extract_model(combined),
        "HasFamilySpec": (packet / "family-spec.csv").exists(),
        "HasValidation": (packet / "validation.csv").exists(),
        "HasCncPlan": (packet / "cnc" / "cnc-plan.json").exists(),
    }


def wolfram_source(packet: Path) -> str:
    meta = metadata(packet)
    family_sample = sample_csv(packet / "family-spec.csv")
    validation_sample = sample_csv(packet / "validation.csv")
    family_json = json.dumps(family_sample)
    validation_json = json.dumps(validation_sample)
    packet_literal = wl_string(str(packet.resolve()))
    meta_assoc = assoc(meta)
    template = """(* instrument-maker-v4.2 Wolfram packet source *)
ClearAll["Global`*"];

packetDir = __PACKET_LITERAL__;
metadata = __META_ASSOC__;

familySpecPath = FileNameJoin[{packetDir, "family-spec.csv"}];
validationPath = FileNameJoin[{packetDir, "validation.csv"}];
cncPlanPath = FileNameJoin[{packetDir, "cnc", "cnc-plan.json"}];

familySpec = If[FileExistsQ[familySpecPath],
  Import[familySpecPath, "Dataset"],
  Dataset[ImportString[__FAMILY_JSON__, "JSON"]]
];

validationData = If[FileExistsQ[validationPath],
  Import[validationPath, "Dataset"],
  Dataset[ImportString[__VALIDATION_JSON__, "JSON"]]
];

frequencyFromMidi[midi_, a4_: 440] := a4*2^((midi - 69)/12);
centsError[measured_, target_] := 1200*Log[2, measured/target];
openPipeLengthIn[freq_, c_: 13552, radius_: 0] := c/(2*freq) - 2*0.6*radius;
stoppedPipeLengthIn[freq_, c_: 13552, radius_: 0] := c/(4*freq) - 0.6*radius;
helmholtzFrequency[area_, volume_, leff_, c_: 13552] :=
  (c/(2*Pi))*Sqrt[area/(volume*leff)];
cantileverFrequency[k_, thickness_, length_] := k*thickness/length^2;
stringFrequency[length_, tension_, linearDensity_] :=
  1/(2*length)*Sqrt[tension/linearDensity];

modelExplorer = Switch[metadata["Model"],
  "Helmholtz",
    Manipulate[
      helmholtzFrequency[portArea, chamberVolume, effectiveLength],
      {{portArea, 0.4, "port area (in^2)"}, 0.05, 4},
      {{chamberVolume, 40, "volume (in^3)"}, 5, 400},
      {{effectiveLength, 0.6, "effective length (in)"}, 0.05, 3}
    ],
  "OpenPipe",
    Manipulate[
      openPipeLengthIn[f, 13552, radius],
      {{f, 440, "target Hz"}, 80, 1200},
      {{radius, 0.375, "bore radius (in)"}, 0, 1.5}
    ],
  "StoppedPipe",
    Manipulate[
      stoppedPipeLengthIn[f, 13552, radius],
      {{f, 220, "target Hz"}, 40, 1000},
      {{radius, 0.375, "bore radius (in)"}, 0, 1.5}
    ],
  "CantileverBeam",
    Manipulate[
      cantileverFrequency[k, thickness, length],
      {{k, 24000, "K constant"}, 1000, 80000},
      {{thickness, 0.25, "thickness (in)"}, 0.05, 1},
      {{length, 4.5, "length (in)"}, 0.5, 24}
    ],
  _,
    Manipulate[
      frequencyFromMidi[midi],
      {{midi, 69, "MIDI note"}, 24, 96, 1}
    ]
];

audioPreview[f_: 440, seconds_: 1.5] :=
  AudioNormalize[
    AudioAdd[
      AudioGenerator[{"Sin", f}, seconds],
      .35 AudioGenerator[{"Sin", 2 f}, seconds],
      .18 AudioGenerator[{"Sin", 3 f}, seconds]
    ]
  ];

validationRows = Normal[validationData];
validationPlot = Quiet@Check[
  ListPlot[
    DeleteMissing[
      ToExpression /@ Lookup[validationRows, "Cents Error", Missing[]]
    ],
    PlotTheme -> "Scientific",
    Frame -> True,
    FrameLabel -> {{"Cents error", None}, {"Measurement row", metadata["PacketName"]}}
  ],
  "No numeric validation cents-error values yet."
];

packetNotebook[] := CreateDocument[
  {
    TextCell[metadata["PacketName"], "Title"],
    TextCell["instrument-maker v4.2 computational packet", "Subtitle"],
    TextCell["Metadata", "Section"],
    ExpressionCell[metadata, "Input"],
    TextCell["Family/design data", "Section"],
    ExpressionCell[familySpec, "Input"],
    TextCell["Model explorer", "Section"],
    ExpressionCell[modelExplorer, "Input"],
    TextCell["Audio preview", "Section"],
    ExpressionCell[audioPreview[440], "Input"],
    TextCell["Validation", "Section"],
    ExpressionCell[validationPlot, "Input"]
  },
  WindowTitle -> metadata["PacketName"]
];

packetNotebook[];
"""
    return (
        template.replace("__PACKET_LITERAL__", packet_literal)
        .replace("__META_ASSOC__", meta_assoc)
        .replace("__FAMILY_JSON__", wl_string(family_json))
        .replace("__VALIDATION_JSON__", wl_string(validation_json))
    )


def write_source(packet: Path, output: Path | None, dry_run: bool) -> Path:
    out = output or packet / "wolfram" / "instrument-model.wl"
    source = wolfram_source(packet)
    if dry_run:
        print(f"--dry-run: would write {out}")
        print(source)
        return out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(source, encoding="utf-8")
    print(out)
    return out


def execute_wolfram(source: Path) -> None:
    wolframscript = shutil.which("wolframscript")
    if not wolframscript:
        raise SystemExit("wolframscript not found; generated .wl source only.")
    subprocess.run([wolframscript, "-file", str(source)], check=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet_dir", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Run wolframscript after writing the .wl source.",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    packet = args.packet_dir
    if not packet.exists():
        raise SystemExit(f"Packet folder not found: {packet}")
    source = write_source(packet, args.output, args.dry_run)
    if args.execute and not args.dry_run:
        execute_wolfram(source)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
