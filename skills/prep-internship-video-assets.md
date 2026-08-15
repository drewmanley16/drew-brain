# Skill: Prep Internship Video Assets

## Purpose
CapCut has no API, so this skill can't touch the actual edit. What it can
do is remove the two slowest manual steps before Drew opens CapCut: typing
captions and hunting down each company's logo one by one.

## When to use
After a script is written with `write-ig-internship-news.md` (or any script
naming multiple companies/logos), before Drew starts editing in CapCut.

## Inputs
- The finished script text
- List of companies/brands mentioned that need a logo pop-in

## Process

### 1. Caption breakdown
Break the full script into caption chunks of 2-3 words each, in speaking
order, lowercase, no punctuation — matches Drew's classic CapCut caption
style (bottom-of-screen, "Aa" text style). Output as a plain numbered list,
one chunk per line, so Drew can read straight down the list while placing
captions in CapCut. Don't try to time-sync it — CapCut's own auto-caption
handles timing off the audio; this list is the reference for how to chunk
it once auto-captions come in.

### 2. Logo check
This environment has no general internet access, so logos can't be
auto-downloaded — this step is a gap check, not a fetch:
1. Check `~/Desktop/company-logos/` for each company mentioned (match on
   filename, case-insensitive, ignore extension).
2. Report which ones already exist (reusable — never ask Drew to re-source
   these) and which ones are missing.
3. For missing ones, tell Drew exactly what to grab (company name) so he
   can save it into that folder — don't guess or fabricate a filename for
   something that isn't there.
4. If Drew pastes/uploads a logo file, save/rename it into
   `~/Desktop/company-logos/{company-lowercase}.png` so the library stays
   consistent for future videos.

### 3. Cue sheet
Output a simple ordered list: company name → logo filename → which line of
the script it should pop in on. This is what Drew actually drags/drops
against in CapCut.

## Output
Three things, in this order:
1. Caption chunk list (numbered, 2-3 words per line)
2. Confirmation of which logos were fetched/already existed/missing
3. Cue sheet (company → logo file → script line)

## Never
Never fabricate a logo URL or save a broken/placeholder image as if it
were the real logo — flag it as missing instead.
