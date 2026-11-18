---
name: next
description: Pick the next roadmap slice item and break it into small steps, without writing the code. Use when the user says "keyingi nima", "nima qilay", "qayerdan boshlay", or asks what to do next.
argument-hint: "[slice number or checklist item, optional]"
---

# Next step

Don't write code and don't create files. The job is to give the user a clear path; the user writes the code.

## 1. Determine the current state

1. Read `docs/roadmap/00 Roadmap.md` (slice tables, checklists, "Know first") and the current slice's spec in `docs/roadmap/0N Phase X - *.md` (Files, Models, Endpoints, Steps, Tests). Also `01 Slice specs - Conventions.md` for layout and API conventions. Look at:
   - which checklist boxes are ticked; the current slice is the lowest-numbered slice with unticked boxes;
   - the slice's **Trigger**: a slice starts when its trigger has happened. Slices run in order; `[later]` items wait until the main flow of the slice works.
2. Check the repo's **actual** state: `git log --oneline -15`, `git status`, and the file tree. Work may be done even though its checkbox is unticked, or the other way around. If you find a mismatch, tell the user.
3. If an argument is given (`$ARGUMENTS`), focus on that slice or item.

## 2. Pick a task

Pick **one** unfinished checklist item (or one spec step) of the current slice, respecting dependencies inside the slice: for example models and migration before the service, the failing race test before the lock. Explain in one sentence why this item and not another.

Follow the slice loop: Flow → simplest solution → break it or measure it → fix → write it down. If the item is a fix (lock, idempotency, index, cache), the step that makes the problem visible (a failing test, a parallel test, a measurement) comes first.

Don't pull in anything a later slice brings (Redis, auth, RLS, CI, Docker image, Celery, cache...). "Nothing is prepared for later slices."

## 3. Output format

Write the answer in Uzbek (Latin script), translating the headings below.

~~~markdown
## Next task: <checklist item> (slice <NN>: <slice name>)

**Why now:** ...

### Steps
1. <concrete action: which file (from the spec's Files list) and what it should contain; not code>
2. ...
(3–7 steps, each 15–60 minutes)

### How you'll know it's done
- [ ] <verifiable criterion: a spec test name that passes, a curl result, a measured number>

### Know first
- <item from the slice's "Know first" list, or a concept>: why it's needed, in one sentence.

### Watch out for
- <2–4 common mistakes in this task>

### When finished
Branch: `<type>/<NN>-<name>`, commit: `<conventional commit example>`, then run `/review-code`.
~~~

Steps say "what" and "why", not "how" (no ready-made code). If the user gets stuck, the `/hint` skill exists.

Give a docs link only if you are sure it is correct (the roadmap's "Know first" links are safe). Otherwise name the section.
