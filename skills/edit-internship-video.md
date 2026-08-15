# Skill: Edit Internship Video

## Purpose
Turn Drew's raw talking-head clips into the finished internship-drop video:
zero dead space, zoom on the opener with a riser, hook + CTA text cards,
word-synced captions, logo pop-ins with a click sound — fully edited, no
CapCut needed for this format.

## Trigger
Drew drops the raw clips into `~/Desktop/internship-videos/` and tells
Claude directly in chat that it's ready. Telegram's inbound bridge was not
reliably reaching the session as of 2026-08-15 — don't assume a Telegram
message will arrive; wait for Drew to say so in chat. (Outbound Telegram,
e.g. the daily cron sending the script, still works fine.)

Drew records multiple short clips (not one continuous take) that get cut
together in sequence, and sometimes re-records a line. Use the `IMG_XXXX`
sequence number to determine actual recording order (more reliable than
file mtime, which resets on copy). If two clips/repetitions say the same
line, use the latest one — check the whole clip for repeats, not just the
first two (a clip can contain 3+ repetitions of a flubbed line).

## Assets (Drew drops these in, check before each edit)
- `~/Desktop/internship-videos/logos/` — company logo files (png/webp/jpeg,
  any format ffmpeg reads). Match by filename to companies named in the
  script, case-insensitive, ignore extension. Report what's missing, don't
  block.
- `~/Desktop/internship-videos/sfx/click.mp3` — logo pop sound
- `~/Desktop/internship-videos/sfx/riser.mp3` — opening-clip buildup sound
(Earlier session notes referenced `~/Desktop/company-logos/` and
`~/Desktop/video-sfx/` — Drew actually uses the paths above, inside the
video folder. Check there first.)

## Tools
- ffmpeg (`/opt/homebrew/bin/ffmpeg`)
- **Transcription: use `whisper` (openai-whisper Python CLI at
  `/opt/homebrew/bin/whisper`), not `whisper-cli`/whisper.cpp** — the
  whisper.cpp install here only has a stub test model that returns empty
  output. `whisper` has `base`/`tiny` cached locally (`~/.cache/whisper/`),
  works offline: `whisper file.wav --model base --output_format json --word_timestamps True --output_dir out --fp16 False --language en`

## Process

1. **Source footage is HDR** (iPhone HLG/BT.2020, 10-bit). Every trim/crop
   must tonemap HDR→SDR or the output looks wrong (crushed contrast,
   wrong color — looks like an unwanted "filter"). Always include this in
   the first filter stage on every clip:
   `zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p`
   followed by the crop, and tag output with
   `-color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv`.
   Carry these same color flags through every subsequent ffmpeg stage
   (zoom, concat, final burn) so nothing drifts again.

2. **Find real speech bounds with actual audio silence detection, not
   word timestamps.** Whisper's word timings lag the true sound onset by
   up to ~0.3-0.9s, which reads as "doesn't start quick enough" / leftover
   dead space. Use:
   `ffmpeg -i clip.MOV -af "silencedetect=noise=-35dB:d=0.05" -f null - 2>&1 | grep silence`
   and take the actual `silence_end`/`silence_start` boundaries around the
   speech you want (down to the millisecond) as your trim points, not
   whisper word start/end. Still use whisper's word-level JSON to figure
   out *what* was said and *which* repetition/take is the clean one — just
   don't use its timestamps for the final cut boundaries.

3. **Zero dead space, including breaths — no exceptions.** If a single
   clip has an internal pause (two sentences in one continuous recording
   with a gap between them), split it into separate sub-clips at the
   silence boundary and concatenate them back-to-back with no gap, rather
   than trimming only the outer edges. There should be no point in the
   final video where he isn't talking.

4. **Normalize + crop** each trimmed segment to portrait 1080x1920 30fps
   (`scale=...force_original_aspect_ratio=increase,crop=1080:1920,fps=30`,
   after the tonemap step above).

5. **Zoom the opening clip**, centered and subtle — 100%→115% linearly
   over its own duration, centered (not corner-anchored, which is
   zoompan's default and looks off):
   `zoompan=z='min(1+0.15*on/FRAMES,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30`
   (FRAMES = clip duration × 30). Re-mux original audio after (zoompan
   drops it).

6. **Riser under the opening clip, timed to its END, not its start.**
   Take the *tail* of `riser.mp3` — its build/climax — sized to exactly
   the opening clip's duration, so the climax lands right on the cut out
   of clip 1: trim riser to its last `clip1_duration` seconds
   (`atrim=start=(riser_total_duration - clip1_duration)`), then
   `amix` it under the clip's original audio.

7. **Concatenate** all segments in order via ffmpeg concat demuxer.

8. **Re-transcribe the assembled video** (same whisper command) — cuts
   shift timing, so caption/logo timestamps must come from the final cut,
   not the per-clip transcriptions.

9. **Build captions** as `.ass`: gap-aware chunking — group consecutive
   words up to 3 at a time, but end the chunk early (even at 1 word) if
   the gap to the next word exceeds ~0.25s, so captions track his actual
   speech rhythm instead of forced fixed-size groups. Lowercase, no
   punctuation, bottom-of-frame (`Alignment 2`, `MarginV ~320` on a
   1920-tall canvas). Cross-check transcribed words against what he's
   actually likely saying and fix obvious mishearings (e.g. whisper
   sometimes hears "rolls" for "roles") rather than transcribing literally.
   Font: **Avenir Next Heavy** — Drew wants Rubik but it isn't installed
   and can't be downloaded (no internet in this environment); swap it in
   if he supplies the font file. All caption/card text is **white**.

10. **Two text cards**, same `.ass`, styled distinctly from captions
    (bigger, top-aligned `Alignment 8`, ~`MarginV 140`): a punchy hook
    line over the first clip's duration, and the literal CTA (e.g.
    `comment "apply"`) over the final clip's duration — pull the actual
    word from the transcript, don't invent one. Both white, same font as
    captions.

11. **Logo pop-ins**: for each company mentioned, find its word-level
    timestamp in the final transcript. Overlay the logo scaled up fast
    (~0.15s pop-in) positioned in the open space **above his head**
    (around `y=H*0.15`) — not over his face — enabled for roughly
    `word_start` to `word_end + 0.35s`. **Cap that end time at the next
    logo's start minus ~0.05s** so consecutive logos (e.g. company names
    said back-to-back) never overlap on screen. Play `click.mp3` at the
    exact `word_start` timestamp (via `adelay` + `amix`), not at clip
    start.

12. **Export** to `~/Desktop/internship-videos/internship-(YYYY-MM-DD).mp4`.
13. Clean up temp working files (`/tmp/...`) when done.

## Known limitation
Clips recorded at different distances from the camera will look like the
"zoom" jumps between cuts even though only clip 1 ever gets an actual zoom
filter applied (confirmed 2026-08-15). This is real framing variance from
how Drew was sitting in each take, not something the pipeline adds. Fixing
it would require face-detection-based auto-reframing to normalize apparent
distance across clips — not currently built. Don't re-diagnose this as a
pipeline bug; ask Drew if it's worth building the reframing step.

## Rules
- High-volume recurring workflow — make editorial judgment calls (take
  selection, trim points, clip order) autonomously and deliver the best
  edit. Don't stop to confirm each cut choice. Drew gives feedback on the
  output, not the plan.
- Never fabricate timing, wording, or CTA text — always derive from the
  actual transcript/audio of Drew's recording.
- If a logo or sfx file is missing, skip it and say so in the summary
  rather than blocking the export.
- Grab a preview frame (`ffmpeg -ss N -frames:v 1 preview.jpg`) of any new
  visual technique before finalizing, to catch problems before Drew has to
  (this is how the HDR color bug and off-center zoom were caught).

## Output
Final MP4 in `~/Desktop/internship-videos/`, named `internship-(date).mp4`,
plus a chat summary of what changed and anything skipped (missing
logos/sfx, font substitution).
