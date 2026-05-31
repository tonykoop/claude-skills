#!/usr/bin/env wolframscript
(* ::Package:: *)

(* wolfram_sync.wls — read the manifest produced by wolfram_inventory.py
   and upload each file to a flat Wolfram Cloud inbox.

   Usage:
     wolframscript -file wolfram_sync.wls -- <manifest.json> [cloud-prefix] [--dry-run]

   Arguments:
     manifest.json   Path to the JSON manifest (required).
     cloud-prefix    CloudObject folder name (default: from manifest, else "GitHub-Inbox").
     --dry-run       Print what would be uploaded; do not actually upload.

   Before running this the first time:
     wolframscript -authenticate
   (one-time browser login to your Wolfram Cloud account).

   What it does:
     For each file in the manifest, uploads it to
        CloudObject["<prefix>/<cloud_name>"]
     with OverwriteTarget -> True. Skips uploads where the cloud object already
     exists AND its byte count matches the local file (cheap idempotency check).
*)

argv = Rest @ $ScriptCommandLine;
(* Strip a literal "--" separator that some wolframscript builds pass through
   to the script. Defensive against shell/platform variation. *)
argv = DeleteCases[argv, "--"];

If[Length[argv] < 1,
  Print["Usage: wolframscript -file wolfram_sync.wls -- <manifest.json> [cloud-prefix] [--dry-run]"];
  Exit[2]
];

manifestPath = First[argv];
restArgs = Rest[argv];
dryRun = MemberQ[restArgs, "--dry-run"];
nonFlagArgs = DeleteCases[restArgs, "--dry-run"];

If[!FileExistsQ[manifestPath],
  Print["ERROR: manifest not found: ", manifestPath];
  Exit[2]
];

manifest = Import[manifestPath, "RawJSON"];
files = Lookup[manifest, "files", {}];
defaultPrefix = Lookup[manifest, "cloud_prefix", "GitHub-Inbox"];
prefix = If[Length[nonFlagArgs] >= 1, First[nonFlagArgs], defaultPrefix];

Print["Manifest:     ", manifestPath];
Print["Cloud prefix: ", prefix];
Print["File count:   ", Length[files]];
Print["Dry run:      ", dryRun];
Print[""];

(* Cloud auth.

   wolframscript -authenticate on WSL/Wolfram-Engine-for-Linux often saves
   credentials at the shell layer but they don't reach the script process,
   so every CloudObject[...] call fires nocred. Workaround: pass user AND
   password via environment variables and call CloudConnect explicitly. *)
If[!dryRun,
  Module[{user, password},
    user = Environment["WOLFRAM_CLOUD_USER"];
    password = Environment["WOLFRAM_CLOUD_PASSWORD"];
    Which[
      StringQ[user] && StringQ[password] && user =!= "" && password =!= "",
        Print["Connecting as ", user, " (using WOLFRAM_CLOUD_USER + WOLFRAM_CLOUD_PASSWORD)..."];
        CloudConnect[user, password],
      StringQ[user] && user =!= "",
        Print["Connecting as ", user, " (saved creds)..."];
        CloudConnect[user],
      True,
        Print["Connecting (saved creds)..."];
        CloudConnect[]
    ];
    If[!$CloudConnected,
      Print[""];
      Print["ERROR: not connected to Wolfram Cloud."];
      Print["Easiest fix — set both env vars and re-run:"];
      Print["  export WOLFRAM_CLOUD_USER=wrfcoin@gmx.com"];
      Print["  read -s -p 'Password: ' WOLFRAM_CLOUD_PASSWORD; export WOLFRAM_CLOUD_PASSWORD; echo"];
      Print["  wolframscript -file wolfram_sync.wls manifest/wolfram_manifest.json"];
      Print["  unset WOLFRAM_CLOUD_PASSWORD"];
      Exit[3]
    ]
  ];
  Print["Connected as: ", $CloudUserID];
  Print[""]
];

joinCloudPath[name_] := If[prefix === "", name, prefix <> "/" <> name];

uploadOne[file_Association, idx_, total_] := Module[
  {localPath, cloudName, cloudPath, co, existing, sizeLocal, sizeRemote, action, result},
  localPath = Lookup[file, "abs_path"];
  cloudName = Lookup[file, "cloud_name"];
  cloudPath = joinCloudPath[cloudName];
  sizeLocal = Lookup[file, "size_bytes", 0];

  If[!FileExistsQ[localPath],
    Print[StringForm["[``/``] MISSING ``  (skipped)", idx, total, localPath]];
    Return["missing"]
  ];

  Print[StringForm["[``/``] ``", idx, total, cloudPath]];

  If[dryRun,
    Print["   (dry-run, no upload)"];
    Return["dry-run"]
  ];

  co = CloudObject[cloudPath];
  (* Cheap idempotency: if a cloud object already exists with the same byte
     length, skip. Notebooks are stored as text, so byte length matches the
     local file for .wl / .nb. *)
  existing = Quiet @ Check[
    Lookup[CloudObjectInformation[co], "ByteCount", Missing["NotFound"]],
    Missing["NotFound"]
  ];
  If[IntegerQ[existing] && existing == sizeLocal,
    Print["   already up-to-date (byte count matches), skipping"];
    Return["skipped"]
  ];

  action = If[IntegerQ[existing], "Updating", "Uploading"];
  Print["   ", action, " (", sizeLocal, " bytes)..."];
  result = Quiet @ CopyFile[localPath, co, OverwriteTarget -> True];
  If[Head[result] === CloudObject,
    Print["   OK"];
    "uploaded",
    Print["   FAILED: ", result];
    "failed"
  ]
];

results = MapIndexed[uploadOne[#1, First[#2], Length[files]] &, files];

counts = Counts[results];
Print[""];
Print["==== Summary ===="];
KeyValueMap[
  Function[{k, v}, Print[StringPadLeft[ToString[v], 4], "  ", k]],
  counts
];

If[KeyExistsQ[counts, "failed"],
  Print["Some uploads failed."];
  Exit[1]
];

Exit[0]
