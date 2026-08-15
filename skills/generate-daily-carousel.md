# Skill: Generate Daily Resource-Drop Carousel

## Purpose
Fully autonomous daily IG carousel: "best youtube videos to learn X" for a
CS/SWE topic. Runs on a cron schedule with no manual step — picks the
topic, researches real videos, builds the images, and writes the caption.
Drew reviews the finished folder and posts it himself.

## Before running
Read `context/content-instagram.md` for voice rules and
`context/content-creation.md` / `context/career.md` for the audience and
topic fit (CS students, early-career SWE, recruiting-adjacent).

## Inputs
- **Background photo**: pull the next unused file (alphabetical) from
  `assets/carousel-backgrounds/inbox/`. If inbox is empty, move everything
  from `assets/carousel-backgrounds/archive/` back into `inbox/` and use
  the first one (recycle the pool — don't stall waiting for new photos).
- **Topic**: top unlogged entry in `projects/carousel-topics.md`'s Queue.
  If the queue is empty, generate 5-10 new topics per that file's Rules
  section before picking one.

## Process

1. **Pick the topic and background** per Inputs above.

2. **Research 4-6 real videos** on the topic:
   - Use WebSearch for "best youtube video/channel to learn <topic>" and
     similar, to find candidate channels with real, current traction.
   - Use `/browse` (never `mcp__claude-in-chrome__*` directly, per global
     config) to open each candidate video's YouTube page, confirm it's a
     real, current, well-subscribed channel (check sub count and that the
     video isn't outdated/broken/removed), and capture a screenshot of the
     video page/thumbnail. Save each screenshot to a temp path.
   - Prefer well-known channels with large, credible followings over
     obscure ones — this is what makes the post feel researched, per
     `context/content-instagram.md`'s specificity rule.
   - Never fabricate a video, channel, or subscriber count. If you can't
     verify a candidate, drop it and find another rather than guessing.
   - Order videos intentionally (e.g. beginner-friendly first, deep-dive
     last) and write a one-line note per video (why it's worth watching,
     what it covers) — not generic filler.

3. **Write the cover/outro text**:
   - Cover: 2-line hook naming the topic, e.g. "best youtube videos" /
     "to learn docker" — matches the example already composed.
   - Outro: forward CTA, e.g. "follow for more" / "free dev resources" —
     no comment-word CTA needed for this format (it's a swipe-through
     resource post, not a link giveaway).
   - Follow `context/content-instagram.md` voice rules: lowercase, no
     hashtags/emoji, no em dashes, specific over generic.

4. **Compose the images**:
   - Create `projects/carousels/YYYY-MM-DD-<topic-slug>/`.
   - Build a config JSON (background, out_dir, tag, cover, outro, videos
     with screenshot paths) per the shape documented at the top of
     `scripts/compose_carousel.py`.
   - Run `python3 scripts/compose_carousel.py <config.json>`.
   - Read back at least the cover slide and one video slide to sanity
     check text isn't clipped/overlapping before calling it done.

5. **Write the caption** as `caption.txt` in the same output folder,
   following the resource-post shape in `context/content-instagram.md`
   (hook, why it matters, the list, follow CTA). Plain lines, no markdown.

6. **House-keeping**:
   - Move the used background photo from `inbox/` to `archive/`.
   - Append a log line to `projects/carousel-topics.md`'s Log section:
     `YYYY-MM-DD — topic — channels used — output folder path`.
   - Remove the topic from the Queue.

## Output
`projects/carousels/YYYY-MM-DD-<topic-slug>/` containing:
- `01-cover.png`, `02..N-video.png`, `NN-outro.png`
- `caption.txt`

Plus a short chat/notification summary: topic, channels featured, and the
output folder path.

## Never
- Never invent a YouTube video, channel, or subscriber count — verify via
  `/browse` before including it.
- Never repeat a topic logged within the last 60 days, or the same channel
  two days running (check the Log in `projects/carousel-topics.md`).
- Never post directly to Instagram — this skill only produces the
  draft folder for Drew to review and post himself.
