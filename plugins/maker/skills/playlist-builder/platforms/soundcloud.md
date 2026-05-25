# SoundCloud platform adapter

SoundCloud has no public write API for personal accounts, so we drive the web UI via Claude in Chrome. The user must be **logged into soundcloud.com in Chrome** before the automation runs.

## Always ask permission first

The automation clicks buttons on the user's behalf. Before running it, confirm:
"I'm about to drive your SoundCloud UI in Chrome to create the playlist '<name>' with <N> tracks. OK to proceed?"

Wait for an explicit yes.

## Creating the playlist (first track)

1. Navigate to the first track's SoundCloud URL.
2. Click the "..." (More) button. The selector is reliable across SoundCloud redesigns:

   ```javascript
   document.querySelector('.listenEngagement .sc-button-more').click();
   ```

3. Wait ~1 second for the dropdown to render.
4. Click **"Add to Playlist"** in the dropdown (the dropdown has two items: "Add to Playlist" and "Station").
5. In the modal that appears, click the **"Create a playlist"** tab.
6. Type the playlist name (e.g. `"37. aparigraha"`).
7. Toggle privacy to **Private** (default is Public — change it).
8. Click **Save**.

## Adding subsequent tracks

For tracks 2 through N:

1. Navigate to the track's SoundCloud URL.
2. Click the "..." button (same selector as above).
3. Wait ~1 second, click "Add to Playlist".
4. The modal opens on the **"Add to playlist"** tab (default). It shows a list of your playlists with name, track count, and privacy badge.
5. If many playlists, use the filter input at the top to find the target by name.
6. Click the target playlist's **"Add to Playlist"** button (it changes to "Added" on success — use that to verify).
7. Close the modal (X button or Escape).
8. Move to the next track.

## Pacing

- 1–2 second waits between major actions (page navigation, modal opening) to let the page render.
- After navigating, wait for the page to fully load before clicking.
- Process tracks **in order** so the playlist preserves the energy arc.

## Failure modes

- **Modal doesn't open:** the page may not have fully loaded. Wait 2 seconds and retry the "..." click.
- **"Add to Playlist" dropdown item missing:** SoundCloud sometimes A/B-tests UI. Fall back to right-clicking the track and looking for an "Add to" option.
- **Logged out mid-flow:** stop, ask the user to re-authenticate, resume from the failed track.
