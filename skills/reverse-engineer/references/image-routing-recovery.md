# Image Routing Recovery

Use this reference during the image-access preflight when a prompt names or implies visual evidence.

## Modes

| `image_access_mode` | Use when | Required first action |
| --- | --- | --- |
| `direct` | The image is rendered to the model/toolchain and can be analyzed directly. | Proceed, but note viewpoint and scale limits. |
| `file-path` | A local file path is available and the runtime can inspect or render it. | Verify the path exists; cite filename and any validation command. |
| `partial` | Some referenced images/views are visible and others are missing. | State which images/views are visible and which are missing. |
| `description-only` | No image is viewable, but the user supplied prose describing it. | Use the degraded banner and cap confidence. |
| `missing` | The prompt references image evidence but no image or usable description is available. | Ask for recovery or explicit approval before analyzing from class knowledge. |

## Degraded Banners

Use the exact banner from `SKILL.md` as the first line of the report. Keep it parseable; do not replace it with a casual disclaimer.

## Runtime Recovery Prompts

### Claude Code

> The prompt references image evidence, but no image is rendered in this runtime. Please save the image to a readable local path, such as `/tmp/object.jpg`, and send me that path. I will inspect the file and label the analysis `image_access_mode=file-path`.

### Codex CLI

> The prompt references image evidence, but this runtime may not receive rendered image attachments. Please provide a readable local image path, reattach the image if the client supports it, or paste a structured description. If we proceed from prose, I will label the analysis `image_access_mode=description-only`.

### Web Vision Runtime

> The image referenced in your message did not arrive in my context. Please reattach it directly in the chat or provide a public/direct link. I will proceed only after confirming whether the image is visible.

### Gemini CLI Text Mode

> The prompt references image evidence, but this text-mode runtime cannot inspect it. Please paste a structured verbal description or provide a local path usable by the available tools. If we continue from prose, the analysis will be degraded and dimension confidence will be capped.

### Mobile Zip Upload

> The prompt references image evidence, but mobile zip-upload paths often strip or hide attachments. Please attach the image directly outside the zip, provide a local/exported path, or paste a structured description. I will record the resulting `image_access_mode`.

## Structured Description Fallback

If the user chooses description-only intake, ask for the smallest useful description:

- Whole-object shape and orientation.
- Visible materials, colors, finishes, fasteners, seams, wear, labels, and damage.
- Any scale reference or known measurement.
- Front/back/left/right/top/bottom differences.
- Close-up details for mechanisms, joints, handles, hinges, straps, ports, or contact surfaces.
- Intended use, load, environment, and safety constraints if the user wants a build handoff.

Description-only output remains provisional by default.
