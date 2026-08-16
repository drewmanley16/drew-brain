# Skill: Generate Daily Resource-Drop Carousel

## Purpose
Fully autonomous daily IG carousel: "best youtube videos to learn X" for a
CS/SWE topic. Runs on a cron schedule with no manual step — picks the
topic, researches real videos, builds the images, and writes the caption.
Drew reviews the finished folder and posts it himself.

## Before running
Read `context/content-instagram.md` for voice rules,
`context/content-creation.md` / `context/career.md` for the audience and
topic fit (CS students, early-career SWE, recruiting-adjacent), and the
config-shape docstring at the top of `scripts/compose_carousel.py` — the
script is the source of truth for exact field names.

## Inputs
- **Background photos**: this run needs one photo per slide (cover +
  one per video + outro). Pull that many unused files (alphabetical) from
  `assets/carousel-backgrounds/inbox/`. If inbox runs short, move
  everything from `assets/carousel-backgrounds/archive/` back into
  `inbox/` and continue (recycle the pool — don't stall waiting for new
  photos). The outro slide does NOT use one of these — see below.
- **Topic**: top unlogged entry in `projects/carousel-topics.md`'s Queue.
  If the queue is empty, generate 5-10 new topics per that file's Rules
  section before picking one.
- **Brand assets** (reusable, not sourced per-run — wire in whichever
  exist, omit the rest, never block on a missing one):
  - `assets/carousel-brand/github-graph.png` → `cover.proof_graphic`
    (background pre-keyed transparent — floats directly on the photo, no
    card/box behind it)
  - `assets/carousel-brand/github-logo-white.png` → `cover.proof_logo`
    (white version so it reads on any photo; the composer places it as a
    fixed top-right watermark, not inline with the graph)
  - `assets/carousel-brand/ig-profile-card.png` → `outro.profile_card`
  - `assets/carousel-brand/outro-photo.png` — the outro's background photo
    is hardcoded to this file inside the composer (falls back to the last
    rotating background only if this doesn't exist). Don't include the
    outro in the `backgrounds` list photo count reasoning — the composer
    handles it automatically.

## Process

1. **Pick the topic and backgrounds** per Inputs above.

2. **Research 4 real videos** on the topic:
   - Use WebSearch for "best youtube video/channel to learn <topic>" and
     similar, to find candidate channels with real, current traction.
     Prefer well-known channels with large, credible followings — this is
     what makes the post feel researched, per
     `context/content-instagram.md`'s specificity rule.
   - `WebFetch` blocks `youtube.com`/`youtu.be` directly (both locally and
     in the cloud sandbox) — verify a video's existence/title/channel by
     cross-referencing WebSearch results (GitHub repos that link the exact
     video ID, Class Central, channel stat sites, etc.), not by fetching
     the YouTube page itself.
   - Never fabricate a video, channel, or subscriber count. If you can't
     verify a candidate, drop it and find another rather than guessing.
   - Order videos intentionally (e.g. beginner-friendly first, deep-dive
     last) and write a 2-3 sentence description per video (what it covers,
     why it's worth watching) — not generic filler.

3. **Fetch real thumbnails** for each verified video — this works even
   where `WebFetch` is blocked, because it's a plain file download, not
   the WebFetch tool:
   ```
   curl -sL "https://img.youtube.com/vi/<VIDEO_ID>/maxresdefault.jpg" -o /tmp/<slug>.jpg
   ```
   Confirm each download actually returned a JPEG (`file /tmp/<slug>.jpg`)
   before using it — a failed fetch sometimes returns a tiny placeholder
   image instead of erroring. If a thumbnail genuinely can't be fetched,
   leave that video's `screenshot` field out rather than guessing a URL.

4. **Write the cover/outro text** as color/underline segments per
   `compose_carousel.py`'s config shape:
   - Cover: 2-line hook naming the topic (e.g. "best youtube videos" /
     "to learn docker", with the topic word in `color: accent`), plus a
     short subtitle line.
   - Outro: 2 lines building to a CTA word in accent color (e.g. "want the
     full list?" / "follow + comment" → `"DOCKER"`).
   - Follow `context/content-instagram.md` voice rules: lowercase-leaning,
     no hashtags/emoji, no em dashes, specific over generic.

5. **Compose the images**:
   - Create `projects/carousels/YYYY-MM-DD-<topic-slug>/`.
   - Build a config JSON: `backgrounds` (cover + one per video + outro,
     see Inputs), `cover`, `outro`, `videos` (each with `rank`, `title`,
     `screenshot`, `description`).
   - Run `python3 scripts/compose_carousel.py <config.json>`. This always
     writes TWO sibling sets automatically — `with-thumbnails/` (real
     screenshots) and `placeholder/` (same layout, thumbnails blanked out
     so Drew can hand-swap one if a fetch was wrong/ugly) — no extra flag
     needed.
   - Read back at least the cover slide and one video slide from
     `with-thumbnails/` to sanity check nothing is clipped, overlapping,
     or has a stray box/border (there should be none — titles and CTA
     text are plain centered stroked text directly on the photo, no pill
     backgrounds, no outline around thumbnails).

6. **Write the caption** as `caption.txt` in the output folder (not inside
   either variant subfolder), following the resource-post shape in
   `context/content-instagram.md` (hook, why it matters, the list, follow
   CTA). Plain lines, no markdown.

7. **House-keeping**:
   - Move each used background photo from `inbox/` to `archive/`.
   - Append a log line to `projects/carousel-topics.md`'s Log section:
     `YYYY-MM-DD — topic — channels used — output folder path`.
   - Remove the topic from the Queue.

## Output
`projects/carousels/YYYY-MM-DD-<topic-slug>/` containing:
- `with-thumbnails/01-cover.png`, `02..N-video.png`, `NN-outro.png`
- `placeholder/` — same filenames, thumbnails blanked
- `caption.txt`

Plus a short chat/notification summary: topic, channels featured, and the
output folder path.

## Never
- Never invent a YouTube video, channel, or subscriber count.
- Never repeat a topic logged within the last 60 days, or the same channel
  two days running (check the Log in `projects/carousel-topics.md`).
- Never post directly to Instagram — this skill only produces the
  draft folder for Drew to review and post himself.
