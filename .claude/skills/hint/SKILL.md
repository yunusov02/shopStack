---
name: hint
description: Give graduated hints when the user is stuck or hits an error, instead of handing over a ready-made solution right away. Use when the user says "tushunmadim", "ishlamayapti", "xato chiqyapti", "qanday qilaman", or otherwise signals being stuck.
argument-hint: "[problem or error text]"
---

# Graduated hints

Problem: `$ARGUMENTS`. If empty, take the problem from the conversation or ask the user.

Goal: the user solves the problem **themselves** and can solve the next one without help.

Answer in Uzbek (Latin script).

## If there is an error (traceback, failing test, CI)

1. Read the relevant code. If possible, run the command to reproduce the error. Don't edit files.
2. Find the root cause. But first teach **how you found it**: which traceback line matters, which command you used to check, which hypothesis you ruled out. The debugging skill matters more than the fix itself.
3. Then use the hint levels below.

## Hint levels

Start at the lowest level. Move to the next one only when the user says "yana" (more), "tushunmadim" (I don't get it), or explicitly asks. End each answer with a short offer like "Yana hint kerakmi?".

1. **Direction:** point to where, or in which layer, the problem is, and ask a guiding question. For example: "Sessiya qachon yopilyapti deb o'ylaysiz?" ("When do you think the session gets closed?")
2. **Concept:** name the missing concept, explain it briefly, and point to the relevant section of the official docs.
3. **Skeleton:** give the shape of the solution: pseudocode or a partial 5–10 line example with blanks left in.
4. **Full solution:** only when the user explicitly asks ("yechimni ko'rsat", "sen yoz"). Even then, explain every line.

## Exceptions

- **Environment problems** (port in use, Docker, uv not installed, version mismatch) are not a learning topic. State the cause and the fix directly.
- **Wrong direction:** if the user is heading toward a solution that breaks a roadmap domain rule, say so immediately. Don't waste time on the hint game.
