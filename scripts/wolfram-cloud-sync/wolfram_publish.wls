#!/usr/bin/env wolframscript
(* ::Package:: *)

(* wolfram_publish.wls — post-upload pipeline. Run AFTER wolfram_sync.wls.

   Safer-by-default: WITHOUT --repos, no objects are made public. Every
   manifest entry gets permission="Private" and cloud_url=null. The map is
   still written so wolfram_emit_engineering_manifest.py has something to
   feed into the per-repo capstone-manifest.json files.

   WITH --repos sambuca,kora (comma-separated list of repo names):
     - For files whose `repo` is in the list:
         SetPermissions[obj, "Public" -> "Execute"]
         Capture cloud URL (from CloudObject's "URL" or First[co])
         permission = "Public-Execute"
     - All other files keep permission="Private", cloud_url=null.

   Empty cloud_prefix (categories mode): the manifest's cloud_name is
   already the full cloud path. Prefix is prepended only when non-empty.

   Output: manifest/wolfram_embed_urls.json — list of records with
   {source_file, cloud_path, cloud_url, permission}.

   Usage:
     wolframscript -file wolfram_publish.wls -- <manifest.json> \\
         [cloud-prefix-override] [--repos a,b,c] [--dry-run]

   Prereq: wolframscript -authenticate. *)

argv = Rest @ $ScriptCommandLine;
argv = DeleteCases[argv, "--"];  (* tolerate explicit -- separator *)

If[Length[argv] < 1,
  Print["Usage: wolframscript -file wolfram_publish.wls -- <manifest.json> [cloud-prefix-override] [--repos a,b,c] [--dry-run]"];
  Exit[2]
];

manifestPath = First[argv];
restArgs = Rest[argv];

dryRun = MemberQ[restArgs, "--dry-run"];

(* Parse --repos value (either "--repos=x,y" or "--repos x,y") *)
reposArg = SelectFirst[restArgs, StringStartsQ[#, "--repos"] &, ""];
publishRepos = Module[{val, idx},
  Which[
    reposArg === "", {},
    StringContainsQ[reposArg, "="],
      val = Last[StringSplit[reposArg, "=", 2]];
      StringSplit[val, ","],
    True,
      idx = FirstPosition[restArgs, "--repos", {0}][[1]];
      If[idx > 0 && idx < Length[restArgs],
        StringSplit[restArgs[[idx + 1]], ","],
        {}
      ]
  ]
];
publishRepos = StringTrim /@ publishRepos;
publishRepoSet = Association[# -> True & /@ publishRepos];

(* Positional prefix override = first non-flag, non-repos-value arg *)
positionalArgs = restArgs;
positionalArgs = DeleteCases[positionalArgs, "--dry-run"];
positionalArgs = DeleteCases[positionalArgs, "--repos"];
positionalArgs = DeleteCases[positionalArgs, _?(StringStartsQ[#, "--"] &)];
(* Drop the repos value if present as the next arg after --repos *)
If[MemberQ[restArgs, "--repos"],
  positionalArgs = DeleteCases[positionalArgs,
    restArgs[[FirstPosition[restArgs, "--repos", {0}][[1]] + 1]],
    1]
];

If[!FileExistsQ[manifestPath],
  Print["ERROR: manifest not found: ", manifestPath];
  Exit[2]
];

manifest = Import[manifestPath, "RawJSON"];
files = Lookup[manifest, "files", {}];
defaultPrefix = Lookup[manifest, "cloud_prefix", ""];
prefix = If[Length[positionalArgs] >= 1, First[positionalArgs], defaultPrefix];

joinCloudPath[name_] := If[prefix === "", name, prefix <> "/" <> name];

PERMISSION = "Public" -> "Execute";

Print["Manifest:        ", manifestPath];
Print["Cloud prefix:    ", If[prefix === "", "(empty — manifest cloud_name is full path)", prefix]];
Print["Files:           ", Length[files]];
Print["Publish repos:   ", If[Length[publishRepos] == 0, "(none — all entries stay Private)", StringRiffle[publishRepos, ", "]]];
Print["Permission:      ", PERMISSION];
Print["Dry run:         ", dryRun];
Print[""];

needsCloud = Length[publishRepos] > 0 && !dryRun;
If[needsCloud,
  Module[{user = Environment["WOLFRAM_CLOUD_USER"],
          password = Environment["WOLFRAM_CLOUD_PASSWORD"]},
    Which[
      StringQ[user] && StringQ[password] && user =!= "" && password =!= "",
        Print["Connecting as ", user, "..."];
        CloudConnect[user, password],
      StringQ[user] && user =!= "",
        CloudConnect[user],
      True, CloudConnect[]
    ];
    If[!$CloudConnected,
      Print["ERROR: not connected. Set WOLFRAM_CLOUD_USER + WOLFRAM_CLOUD_PASSWORD env vars and retry."];
      Exit[3]
    ];
    Print["Connected as: ", $CloudUserID];
    Print[""]
  ];
];

publishOne[file_Association, idx_, total_] := Module[
  {cloudName, cloudPath, repo, co, urlValue, permResult, record, shouldPublish},
  cloudName = Lookup[file, "cloud_name"];
  cloudPath = joinCloudPath[cloudName];
  repo = Lookup[file, "repo", ""];
  shouldPublish = KeyExistsQ[publishRepoSet, repo];

  record = <|
    "source_file" -> Lookup[file, "rel_path", ""],
    "repo"        -> repo,
    "cloud_path"  -> cloudPath,
    "cloud_url"   -> Null,
    "permission"  -> "Private"
  |>;

  Print[StringForm["[``/``] ``  (``)", idx, total, cloudPath,
    If[shouldPublish, "publishing", "private"]]];

  If[!shouldPublish,
    Return[record]
  ];

  If[dryRun,
    Print["   (dry-run, no permission/URL changes)"];
    record["permission"] = "would-publish";
    Return[record]
  ];

  co = CloudObject[cloudPath];
  (* Wolfram 14.x: CloudObjectInformation returns CloudObjectInformationData,
     not a plain Association — accept both for the existence check. *)
  If[!MemberQ[{Association, CloudObjectInformationData},
        Head[Quiet @ CloudObjectInformation[co]]],
    Print["   SKIP: cloud object not found (run wolfram_sync.wls first?)"];
    record["permission"] = "missing";
    Return[record]
  ];

  (* 14.x SetPermissions returns a List (of permission rules) on success,
     a Failure/$Failed on error. *)
  permResult = Quiet @ SetPermissions[co, PERMISSION];
  If[!FailureQ[permResult] && permResult =!= $Failed,
    record["permission"] = "Public-Execute";
    Print["   permissions: ", PERMISSION, " OK"],
    Print["   permissions: FAILED ", permResult];
    record["permission"] = "failed"
  ];

  urlValue = Quiet @ CloudObjectInformation[co, "URL"];
  If[!StringQ[urlValue], urlValue = First[co, Null]];
  If[StringQ[urlValue],
    record["cloud_url"] = urlValue;
    Print["   url: ", urlValue],
    Print["   url: NOT FOUND"]
  ];

  record
];

records = MapIndexed[publishOne[#1, First[#2], Length[files]] &, files];

manifestDir = DirectoryName[manifestPath];
outputPath = FileNameJoin[{manifestDir, "wolfram_embed_urls.json"}];

If[!dryRun,
  Export[outputPath, records, "RawJSON"];
  Print[""];
  Print["Wrote: ", outputPath];
  Print["Records: ", Length[records]];
  publicCount = Count[records, r_ /; Lookup[r, "permission"] === "Public-Execute"];
  Print["Public-Execute: ", publicCount, "  Private: ", Length[records] - publicCount];
];

Exit[0]
