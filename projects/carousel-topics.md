# Project: Daily Resource-Drop Carousel

## Purpose
Track topic history and queue for the daily auto-generated IG carousel
("best youtube videos to learn X"). Keeps the cron-driven skill
(`skills/generate-daily-carousel.md`) from repeating a topic or channel
too soon.

## Queue (upcoming, pick top unlogged one each run)
- docker
- git internals / rebasing
- system design basics
- SQL joins & indexing
- Redis
- Kubernetes fundamentals
- REST vs GraphQL
- OAuth / auth flows
- CI/CD pipelines
- Big-O / algorithm complexity
- React hooks
- Postgres performance
- Kafka / event streaming
- Terraform basics
- Linux command line

## Log (most recent first)
Format: `YYYY-MM-DD — topic — channels used — output folder`

<!-- entries added by the daily skill go here -->

## Rules
- Don't repeat a topic that's in the log within the last 60 days.
- Don't feature the same YouTube channel two days in a row.
- If the queue runs dry, generate 5-10 new topic ideas consistent with
  `context/career.md` / `context/content-creation.md` (CS, AI, SWE,
  recruiting, system design) and append them to the queue instead of
  stalling.
