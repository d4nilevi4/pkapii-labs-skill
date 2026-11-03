---
name: lab-helper
description: Field notes for a student doing hands-on infrastructure labs (Docker, Docker Compose, Kubernetes with kind) inside a VM on an Apple Silicon Mac, using the student's own assignment files. Use when the user works on such labs (course on software-defined application and infrastructure architecture, PKAPII), sets up VirtualBox/Ubuntu ARM VMs on an M-series Mac, debugs Compose/kind/kubectl in a lab, or needs real evidence (logs, screenshots) from commands. Contains setup methods and pitfalls only: no assignment text, no report template, no finished work.
---

# Lab helper

Support notes from a real run of such labs. They explain how to set things up and what breaks. They do not contain the assignments, answers, or a report layout.

## Tell the user first (once per session, in their language)

1. The notes come from labs done on an **Apple Silicon Mac** with **VirtualBox 7.2.x** and an **Ubuntu 22.04 ARM64** guest. Other hosts need adapted commands.
2. Reports produced in that original run were **not formatted per the Russian state standard (GOST)** and would not be accepted as they were. This skill gives no report formatting. The user must get the department's requirements and check the result themselves.
3. Assignment files are not included. The user puts their own copies into the folder Claude is opened in.
4. They should check their course's rules on AI assistance. The work and its understanding must be theirs.

## Rules

- **Assignments.** Find them in the working directory (docx: `textutil -convert txt -stdout f.docx` or pandoc; pdf: `pdftotext`). Read every file fully, turn it into a checklist of required steps, requirements for the report and control questions, and ask when something is unclear. Never copy assignment text into a public place or into this repository.
- **The student drives.** Explain what each step does and why. Let the user choose tools and wording. Help them understand control questions; do not hand over ready answers to copy. Do not offer a report layout, markup or template. If they want help with a report, ask for their required structure and let them decide how to produce it.
- **Real evidence only.** Logs and screenshots must come from commands that actually ran. Never invent output. If an image is rendered from a transcript (not a screen capture), or a command ran without a recorded output, the report must say so. See `references/evidence.md`.
- **Safety.** Passwordless sudo only inside the lab VM. Never change host security settings, never ask for the host password, never print API keys or tokens, never send email or messages for the user. Ask before deleting anything outside the lab.
- **Personal data.** Ask the user for names, groups or usernames when needed; use placeholders in notes and files that could be shared.

## Workflow

1. **Inventory.** List the assignment files, build the checklist, note version numbers and architectures the assignment assumes (often amd64 and outdated).
2. **Environment.** `uname -m`, `VBoxManage --version`, `brew list`. On Apple Silicon read `references/vm-apple-silicon.md` before touching VirtualBox. Never try an amd64 image there.
3. **Do the steps one at a time.** Run each command through a recorded transcript (`scripts/vmrun.py`, see `references/evidence.md`). Before a Docker or Compose lab read `references/docker-notes.md`; before a Kubernetes lab read `references/kubernetes-notes.md`.
4. **Keep a problem log** while working: time, symptom, cause, fix. It also teaches the student and feeds an honest "problems" section.
5. **Verify.** When a lab is done, compare every checklist item with real evidence, and every claim in the user's text with a log. If sub-agents are available, use a separate fresh one for this. Check that no two figures are the same image (`md5`) and each shows what its caption says.
6. **Clean up only when asked:** shut the VM down with `acpipowerbutton`, then delete it (`references/vm-apple-silicon.md`, last section).

## Habits that avoid most pain

- Quote URLs in zsh (`?` is a glob).
- Never pipe state-changing commands into `head`: it closes the pipe and kills the command.
- On macOS `sed -i ''` needs the empty suffix.
- Adjust every command from an old assignment for `arm64` and the real Ubuntu release (`jammy`, not `focal`).
- Do not read this skill's reference files unless the task needs them; they are written to be loaded on demand.
