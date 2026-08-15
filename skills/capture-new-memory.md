# Skill: Capture New Memory

## Purpose

Decide whether new information belongs in Drew's personal brain and store it in the right place.

## Store When

Information is:

- likely to matter again
- a meaningful decision
- a durable preference
- a new project or major project update
- a long-term goal
- a repeated workflow
- important context about a professional relationship
- a lesson Drew explicitly wants to remember

## Do Not Store

- random one-off questions
- temporary details with no future value
- every conversation verbatim
- easily searchable public facts
- jokes that do not affect future behavior

## Routing

- decision → `memory/decisions.md`
- person → `memory/people.md`
- lesson → `memory/lessons.md`
- unprocessed note → `memory/inbox.md`
- project state → relevant `projects/*.md`
- stable personal preference → `identity/*.md`

## Entry format

Match the existing format in each file rather than inventing a new one.

`memory/decisions.md` entries:
```
## YYYY-MM-DD — Title

**Decision:** what was decided.

**Why:** the reasoning (only if non-obvious).
```

`memory/people.md` entries use the template already in that file — fill in
Relationship, Context, Last meaningful interaction, Things to remember,
Follow-up. Skip fields with nothing useful to say.

`memory/lessons.md` and `memory/inbox.md`: one dated bullet or short
paragraph, terse, no filler.

`projects/*.md`: add to the relevant existing section (e.g. "Track Here" in
`projects/drewisliving.md`) rather than creating new sections per update.

## Worked examples (from real sessions)

- Drew negotiated a sponsorship rate down from an initial ask to a specific
  number with PracHub → **decision**, logged in `memory/decisions.md` if
  it sets a pricing precedent (e.g. "Drew's baseline rate for a dedicated
  Reel collab is ~$225-300"), not logged at all if it's a one-off amount
  with no future bearing.
- Drew's PayPal internship wrapped with a return offer still pending →
  **project state**, goes in `projects/paypal.md`, with a follow-up note
  to update once the decision comes in.
- Drew mentioned his boss Deva made the internship what it was →
  **person**, goes in `memory/people.md` if Drew is likely to work with or
  reference Deva again (e.g. as a reference, LinkedIn recommendation).
- Drew gets a daily internship-openings email from swelist.com → **stable
  workflow/tool**, goes in `context/content-instagram.md` or
  `projects/drewisliving.md` as a sourcing method, not memory — it's
  already documented where it's used.
- A one-off joke about a $6.50 miso latte → **do not store**, no future
  value.

## Never

Never store secrets, API keys, tokens, or credentials seen in emails, code,
or conversation, even in `memory/inbox.md`.
