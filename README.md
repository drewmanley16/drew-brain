# Drew Brain

A portable personal knowledge and skill system for AI.

The goal of this repository is to make AI increasingly useful by giving it owned context about Drew, reusable operating procedures, project state, and durable memory.

## Core Idea

`frontier model + owned context + skills + tools + memory = personal AI`

The model can change. The valuable asset is the context and procedures that stay with you.

## Structure

```text
identity/    stable information about who Drew is and how he prefers to work
context/     changing background that is useful across tasks
skills/      reusable procedures for recurring work
projects/    state and context for active long-running projects
memory/      decisions, lessons, people, and unprocessed notes
```

## How to Use This Repo

1. Load the relevant identity files when an AI needs to understand Drew's preferences.
2. Load project/context files only when they are relevant to the current task.
3. Use a file in `skills/` as the procedure for recurring work.
4. Capture meaningful new information using `skills/capture-new-memory.md`.
5. Periodically clean `memory/inbox.md` and route useful information into the correct file.

## Rule for New Skills

If Drew has to explain how he wants the same kind of task done more than twice, consider turning that workflow into a skill.

## Security

Do not put API keys, passwords, private company information, confidential documents, or other secrets in this repository.
