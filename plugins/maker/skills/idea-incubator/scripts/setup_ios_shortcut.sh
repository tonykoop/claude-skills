#!/usr/bin/env bash
# setup_ios_shortcut.sh — Print the Obsidian Advanced URI pattern for the
# iOS Shortcut "Gemini → Obsidian Inbox" (Story #407, Epic #406).
#
# Usage:
#   ./setup_ios_shortcut.sh [--vault VAULT_NAME]
#
# Output: the URI template to paste into the iOS Shortcuts "Text" action
# (Action 7 in references/mobile-capture-bridge.md). Copy the printed URI
# into your Shortcut; replace placeholder text in square brackets at runtime.
#
# The stable filename stem (gemini-<sha8>-<slug>) is derived at clip-time by
# url_upsert.py; the Shortcut uses the URL-encoded chat URL as a fallback stem
# that url_upsert.py normalizes during ingestion.

set -euo pipefail

VAULT="Tony"

while [[ $# -gt 0 ]]; do
    case $1 in
        --vault)
            VAULT="$2"
            shift 2
            ;;
        *)
            echo "Usage: $0 [--vault VAULT_NAME]" >&2
            exit 1
            ;;
    esac
done

cat <<EOF
=========================================================
iOS Shortcut — Gemini → Obsidian Inbox
Vault: ${VAULT}
Inbox folder: Inbound_Brainstorms
=========================================================

Paste the text below into Action 7 ("Build Obsidian URI") of your Shortcut.
Replace the bracketed variables with Shortcut variables from earlier actions.

--- COPY FROM HERE ---
obsidian://advanced-uri?vault=${VAULT}&filepath=Inbound_Brainstorms%2Fgemini-[EncodedURL].md&data=[EncodedContent]&mode=new
--- COPY TO HERE ---

Steps recap (see references/mobile-capture-bridge.md for full details):
  Action 1  Receive URLs/Text from Share Sheet
  Action 2  Get Text from Input → store as raw URL
  Action 3  URL Encode [raw URL] → EncodedURL
  Action 4  Format Date (ISO 8601) → ISODate
  Action 5  Build front-matter text block → FrontMatter
  Action 6  URL Encode [FrontMatter] → EncodedContent
  Action 7  Text: the URI above → ObsidianURI
  Action 8  Open URLs: [ObsidianURI]

After setup, enable "Show in Share Sheet" in the Shortcut's ⓘ settings.
=========================================================
EOF
