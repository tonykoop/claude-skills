#!/usr/bin/env wolframscript
(* ::Package:: *)

(* wolfram_orphans.wls — diff cloud objects under the prefix against the
   local manifest; report or delete orphans.

   "Orphan" = a CloudObject under <prefix>/ whose name is NOT in the current
   manifest's cloud_name set. This happens after a local rename (the old
   cloud objects are dangling) or after deleting a local file.

   Usage:
     wolframscript -file wolfram_orphans.wls -- <manifest.json> [cloud-prefix] \\
         [--delete]

   Default mode lists orphans; pass --delete to remove them.

   Prereq: wolframscript -authenticate. *)

argv = Rest @ $ScriptCommandLine;
argv = DeleteCases[argv, "--"];  (* tolerate explicit -- separator *)

If[Length[argv] < 1,
  Print["Usage: wolframscript -file wolfram_orphans.wls -- <manifest.json> [cloud-prefix] [--delete]"];
  Exit[2]
];

manifestPath = First[argv];
restArgs = Rest[argv];
doDelete = MemberQ[restArgs, "--delete"];
nonFlagArgs = Select[restArgs, !StringStartsQ[#, "--"] &];

If[!FileExistsQ[manifestPath],
  Print["ERROR: manifest not found: ", manifestPath];
  Exit[2]
];

manifest = Import[manifestPath, "RawJSON"];
files = Lookup[manifest, "files", {}];
defaultPrefix = Lookup[manifest, "cloud_prefix", "GitHub-Inbox"];
prefix = If[Length[nonFlagArgs] >= 1, First[nonFlagArgs], defaultPrefix];

expectedNames = Lookup[#, "cloud_name"] & /@ files;
expectedSet = Association[# -> True & /@ expectedNames];

Print["Manifest:        ", manifestPath];
Print["Cloud prefix:    ", prefix];
Print["Expected files:  ", Length[expectedNames]];
Print["Mode:            ", If[doDelete, "DELETE orphans", "list only"]];
Print[""];

Module[{user = Environment["WOLFRAM_CLOUD_USER"],
        password = Environment["WOLFRAM_CLOUD_PASSWORD"]},
  Which[
    StringQ[user] && StringQ[password] && user =!= "" && password =!= "",
      CloudConnect[user, password],
    StringQ[user] && user =!= "", CloudConnect[user],
    True, CloudConnect[]
  ];
  If[!$CloudConnected,
    Print["ERROR: not connected. Set WOLFRAM_CLOUD_USER + WOLFRAM_CLOUD_PASSWORD env vars."];
    Exit[3]
  ];
  Print["Connected as: ", $CloudUserID];
  Print[""];
];

(* In categories mode the prefix is empty and the actual top-level folder
   is derived from the manifest's cloud_names — typically "Musical_Instruments"
   plus optionally "WSS-2019". Probe both. *)
listAtRoot[root_] := Module[{r},
  r = Quiet @ CloudObjects[CloudObject[root]];
  If[ListQ[r], r, {}]
];

allObjs = If[prefix === "",
  Module[{roots},
    roots = DeleteDuplicates[Cases[
      Lookup[#, "cloud_name", ""] & /@ files,
      _?(StringContainsQ[#, "/"] &) :> First[StringSplit[#, "/", 2]]
    ]];
    Flatten[listAtRoot /@ roots]
  ],
  listAtRoot[prefix]
];

If[!ListQ[allObjs] || Length[allObjs] == 0,
  Print["WARN: no cloud objects found. Either nothing has been synced, or the prefix(es) are wrong."];
  Exit[0]
];

Print["Cloud objects under prefix: ", Length[allObjs]];

(* In categories mode the prefix is "" and cloud_name is already the full
   path (e.g. "Musical_Instruments/strings/sambuca/..."). In flat-inbox
   mode it's just the basename and the prefix is the folder. *)

orphans = {};
Do[
  Module[{path, parts, name},
    path = Lookup[CloudObjectInformation[obj], "Path", ""];
    name = If[prefix === "",
      (* Categories mode: compare the full path *)
      path,
      (* Flat-inbox: strip "<user>:<prefix>/" prefix to get the basename *)
      (parts = StringSplit[path, prefix <> "/", 2];
       If[Length[parts] >= 2, Last[parts], ""])
    ];
    If[name =!= "" && !KeyExistsQ[expectedSet, name],
      AppendTo[orphans, <|"name" -> name, "object" -> obj, "path" -> path|>]
    ]
  ],
  {obj, allObjs}
];

Print["Orphans found: ", Length[orphans]];
If[Length[orphans] == 0,
  Print["Nothing to do."];
  Exit[0]
];

Print[""];
Print["Orphan list:"];
Do[Print["  ", Lookup[o, "name"]], {o, orphans}];

If[!doDelete,
  Print[""];
  Print["(list-only) Pass --delete to remove these objects."];
  Exit[0]
];

(* Delete pass *)
Print[""];
Print["Deleting ", Length[orphans], " orphans..."];
deleted = 0;
failed = 0;
Do[
  Module[{result},
    result = Quiet @ DeleteFile[Lookup[o, "object"]];
    If[result === Null,
      Print["  DELETED ", Lookup[o, "name"]];
      deleted++,
      Print["  FAILED  ", Lookup[o, "name"], "  ", result];
      failed++
    ]
  ],
  {o, orphans}
];
Print[""];
Print["Deleted: ", deleted, "   Failed: ", failed];
If[failed > 0, Exit[1]];
Exit[0]
