# Skill: Edit Internship Video

## Purpose
Turn Drew's raw talking-head recording (sent via Telegram) into the
finished internship-drop video: subtitles, logo pop-ins, zoom/riser on the
opening clip — fully edited and dropped on the Desktop, no CapCut needed
for this format.

## Trigger
Drew sends a raw video via Telegram after recording against a script from
`write-ig-internship-news.md` / the daily cron. Download it with the
Telegram plugin's `download_attachment`.

## Requires
- ffmpeg and whisper-cli (confirmed installed locally)
- `~/Desktop/company-logos/` — logo PNGs for companies mentioned (check
  first, per `prep-internship-video-assets.md`; if any are missing, tell
  Drew and proceed without that logo rather than blocking)
- `~/Desktop/video-sfx/pop.mp3` — logo reveal sound (Drew-supplied)
- `~/Desktop/video-sfx/riser.mp3` — hook buildup sound (Drew-supplied)
- The script text this recording was read from, for caption alignment

## Process

1. **Transcribe** the raw video with `whisper-cli` to get word-level
   timestamps (use `--word_timestamps true` / output `.json` or `.srt`
   depending on the whisper-cli build — check `whisper-cli --help` if the
   flags differ from expected).
2. **Build captions**: group words into 2-3 word chunks in speaking order
   using the real timestamps from transcription (not estimated timing).
   Format as SRT, positioned near the bottom of frame (5/6 down), lowercase,
   no punctuation — matches the "classic" CapCut caption look Drew wants.
3. **Opening clip treatment**: on the first clip/shot (from the start of
   the video to the first cut, or the first ~2-3 seconds if there's no
   scene change), apply a zoom from 100% to 130% over its duration
   (`zoompan` or `scale`+`crop` filter in ffmpeg). Layer `riser.mp3` under
   this same span, fading/ending around the transition point.
4. **Logo pop-ins**: for each company mentioned in the script, overlay its
   PNG from `~/Desktop/company-logos/` timed to when it's said (use the
   transcription timestamps to find when that word occurs), with a quick
   scale-in (pop) animation and `pop.mp3` played at that timestamp.
5. **Burn it all together** with ffmpeg: base video + burned-in SRT +
   logo overlays (`overlay` filter, timed with `enable='between(t,X,Y)'`) +
   mixed audio (original audio + riser + pop sounds at their timestamps).
6. **Export** to `~/Desktop/internship-(YYYY-MM-DD).mp4` using today's date.
7. **Reply on Telegram** confirming it's done and where to find it.

## Rules
- Never fabricate timing — always derive caption and logo-pop timestamps
  from the actual whisper transcription of Drew's recording, not from
  guessing based on the script's word order alone (he may pause, restart,
  or ad-lib).
- If a logo or sound effect is missing, skip that element and say so in
  the Telegram reply rather than silently failing or blocking the whole
  export.
- If the recording doesn't clearly match the script that was sent (very
  different wording), flag it rather than forcing alignment.

## Output
Final MP4 on Desktop, named `internship-(date).mp4`, plus a Telegram reply
summarizing what was included (captions, which logos, which sfx) and
flagging anything skipped.
