# Image-Access Recovery Prompts

Use this reference when the workflow's image-access preflight (step 0) finds `image_access_mode` is `missing` or `partial`. Ask **once** for recovery using the script for the user's runtime, then accept their answer and proceed under the resulting mode.

The goal is *not* to badger the user. It is to give them one clear, runtime-appropriate option to upgrade the intake before the analysis is locked into prose-only confidence caps.

## How to choose a script

| Runtime signal | Use the script for |
| --- | --- |
| `claude-code` CLI (this is what you usually are) | Claude Code |
| `codex` CLI without vision | Codex CLI |
| Web app at `claude.ai` with vision available | Web vision |
| `gemini` CLI in text mode | Gemini CLI text |
| Mobile / phone-shared zip / pasted-link-only | Mobile zip-upload |

If you cannot tell which runtime you are in, default to the Claude Code script — its file-path option is the broadest fallback.

## Claude Code

```text
I can't see the image you mentioned in this pane. To get the highest-confidence
analysis, can you re-share it as a file path I can read with my Read tool?

Examples:
  - /mnt/c/Users/<you>/Downloads/<file>.jpg   (WSL view of Windows path)
  - /home/<you>/screenshots/<file>.png        (native Linux/macOS path)
  - ~/Documents/<file>.heic                   (works either way)

If a file path isn't workable, I can also use:
  - a public URL I can fetch with WebFetch
  - your written description (I'll proceed in description-only mode and
    cap dimensional confidence per the skill rules)

Tell me which option you'd like and I'll continue.
```

## Codex CLI (no vision)

```text
The Codex CLI session can't render images directly, even when one is attached.
To upgrade beyond description-only mode, please either:

  1. Save the image to a local path and tell me the path. I can read EXIF and
     basic metadata via shell tools but not pixels — so I'll still mark this
     as `file-path` (not `direct`) until a vision-capable runtime confirms.
  2. Open a parallel Claude Code or web pane that *can* view the image and
     paste the structured observation back here.
  3. Describe the object in prose; I'll proceed in description-only mode with
     the standard confidence caps.

Which one do you want?
```

## Web vision (claude.ai with images enabled)

```text
The image you referenced didn't render in my pane — usually because the
upload was stripped or the file type isn't supported here. Could you:

  1. Re-attach as JPG, PNG, GIF, or WEBP under 5 MB and try again, or
  2. Paste a public URL I can fetch, or
  3. Describe it in prose (I'll proceed in description-only mode).

If you re-attach successfully I'll switch to direct mode and produce the
full-confidence analysis.
```

## Gemini CLI text mode

```text
This Gemini CLI session is in text mode and won't render image attachments.
Options:

  1. Switch to a vision-capable session and re-run the request, or
  2. Save the image locally and provide a path; I'll work in `file-path`
     mode (metadata only, no pixels), or
  3. Describe the object in prose — I'll proceed in description-only mode
     with the standard confidence caps.

Which do you prefer?
```

## Mobile zip-upload (attachments stripped)

```text
Looks like the mobile flow stripped the image attachment — that happens with
zip uploads and some link previews. To get a confident analysis, you can:

  1. From a desktop, drop the original file into a new turn, or
  2. Send a direct public URL (Imgur, Drive share, etc.) I can fetch, or
  3. Describe the object in prose — I'll proceed in description-only mode.

Option 1 gives the best result. Tell me which one you'd like.
```

## After the user answers

Record the outcome in the observation ledger's `intake:` block:

| User did | Set `image_access_mode` to | Set `recovery_path` to |
| --- | --- | --- |
| Re-attached and you can now see pixels | `direct` | `requested-and-supplied` |
| Gave a file path you read with the Read tool, but didn't render pixels | `file-path` | `requested-and-supplied` |
| Declined / said "just go with the description" | `description-only` | `requested-and-declined` |
| Gave only the object's name | `named-object` | `requested-and-declined` |
| Some images now visible, others still missing | `partial` | `requested-and-supplied` |

Then emit the degraded-mode banner if the resulting mode is anything other than `direct`, and proceed with the normal workflow.

## Don't ask twice

If the user has already declined recovery in this session, do not re-prompt on the next turn. Continue under the chosen mode. The user can always manually invite a re-prompt by attaching a fresh image.
