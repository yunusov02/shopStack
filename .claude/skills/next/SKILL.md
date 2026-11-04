---
name: next
description: Pick the next roadmap task and break it into small steps, without writing the code. Use when the user says "keyingi nima", "nima qilay", "qayerdan boshlay", or asks what to do next.
argument-hint: "[stage or task name, optional]"
---

# Next step

Don't write code and don't create files. The job is to give the user a clear path; the user writes the code.

## 1. Determine the current state

1. Read `docs/retail-saas-roadmap.md` and the matching `docs/tasks/stage-NN-*.md` file (small tasks with IDs like `S3.T07`, each with a "Must know" line) and look at:
   - which checkboxes are ticked;
   - each stage's prerequisites ("Prerequisites");
   - the MVP line: level 1 `[CORE]` tasks come first (stages 0, 1, 2, 3, 5, 9, 10).
2. Check the repo's **actual** state: `git log --oneline -15`, `git status`, and the file tree. Work may be done even though its checkbox is unticked, or the other way around. If you find a mismatch, tell the user.
3. If an argument is given (`$ARGUMENTS`), focus on that task.

## 2. Pick a task

Pick **one** unfinished `[CORE]` task from the current stage, respecting dependencies: for example, tooling comes before writing code, and the DB layer comes before the readiness endpoint. Explain in one sentence why this task and not another.

## 3. Output format

Write the answer in Uzbek (Latin script), translating the headings below.

~~~markdown
## Next task: <name> (<stage>, [CORE])

**Why now:** ...

### Steps
1. <concrete action: which file and what it should contain; not code>
2. ...
(3–7 steps, each 15–60 minutes)

### How you'll know it's done
- [ ] <verifiable criterion, e.g. "`curl localhost:8000/health/live` returns 200">

### Concepts to learn
- <concept>: why it's needed, in one sentence, with the relevant section of the official docs.

### Watch out for
- <2–4 common mistakes in this task>

### When finished
Branch: `<type>/<stage>-<name>`, commit: `<conventional commit example>`, then run `/review-code`.
~~~

Steps say "what" and "why", not "how" (no ready-made code). If the user gets stuck, the `/hint` skill exists.

Give a docs link only if you are sure it is correct. Otherwise name the section.
