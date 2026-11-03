---
name: lab-helper
description: Field notes for hands-on infrastructure labs (Docker, Docker Compose, Kubernetes with kind) done in a VM on an Apple Silicon Mac from a student's own assignment files. Covers VirtualBox/Ubuntu ARM VM setup, Docker/Compose/kind pitfalls and fixes, and capturing real command output and screenshots. Relevant for a course on software-defined application and infrastructure architecture (PKAPII). Contains setup methods and lessons only: no assignment text, no report template, no finished work.
---

# Lab helper

Notes from a real run of such labs. They describe how the environment was set up, what broke, and how it was fixed.

## Context

- Host: Apple Silicon Mac. Hypervisor: VirtualBox 7.2.x. Guest: Ubuntu 22.04 ARM64. Other hosts need adapted commands.
- The reports from that run were not formatted per the Russian state standard (GOST) and would not be accepted as they were. This skill contains no report formatting, template or markup; the format comes from the student's department.
- Assignment files are not included because they are copyrighted. The student puts their own copies (docx, pdf) into the folder Claude is opened in. They can be read with `textutil -convert txt -stdout f.docx`, pandoc or `pdftotext`.
- There is no personal data here. Names, groups and usernames appear only as placeholders.

## Contents

| File | What it describes |
|---|---|
| `references/vm-apple-silicon.md` | Creating, installing, networking and deleting an ARM Ubuntu VM in VirtualBox on Apple Silicon, with the known hangs and their fixes |
| `references/docker-notes.md` | Docker and Compose on an ARM guest: installation, PostgreSQL volumes, networks, healthchecks, proxy errors |
| `references/kubernetes-notes.md` | kind on ARM, reaching a NodePort from the Mac, `kubectl` pitfalls, a general method for diagnosing a broken deployment |
| `references/evidence.md` | Recording real command output and rendering terminal screenshots from it |
| `scripts/vmrun.py`, `scripts/termshot.py` | Run commands in the VM or on the host, save the transcript, render a PNG from it |

The reference files are meant to be read on demand, one per topic.

## How the original run went

1. The assignment files were read in full and turned into a checklist of steps, report requirements and control questions.
2. The environment was checked (`uname -m`, `VBoxManage --version`) and an ARM VM was built from the notes above.
3. Every command ran through a recorded transcript, so each figure had a log behind it.
4. A timestamped problem log (symptom, cause, fix) was kept along the way.
5. A separate fresh reviewer compared checklist items and the report text with the logs and looked for duplicate or misleading figures.
6. At the end the VM was shut down gracefully (`acpipowerbutton`) and removed (`unregistervm --delete`).

Safety facts from that run: passwordless sudo existed only inside the lab VM, host security settings were not touched, API keys were not printed, and no messages were sent on the student's behalf.

## Habits that saved time

- Quote URLs in zsh (`?` is a glob).
- Piping a state-changing command into `head` closes the pipe and kills the command.
- On macOS `sed -i ''` needs the empty suffix.
- Commands from older assignments needed `arm64` and the real Ubuntu release (`jammy`, not `focal`).
