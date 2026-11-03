# Capturing real evidence (logs and screenshots)

Goal: every figure in the student's report comes from something that really ran, and the student can say exactly how it was made.

## Pattern

`scripts/vmrun.py` runs commands in the VM over SSH (or on the host with `--host`), saves the exact transcript, and renders a terminal-style PNG from that transcript.

```bash
export LAB_SSH_USER=<user> LAB_SSH_KEY=vm/id_lab LAB_SSH_PORT=2222 LAB_OUT=evidence
python3 scripts/vmrun.py 01_versions --cwd '~/project' "docker --version" "docker compose version"
```

- One call = one figure. Name it by number and meaning (`07_compose_up`). The `.txt` next to the `.png` is the proof.
- Stderr is merged into stdout, so the order is the one a real terminal shows.
- The image is **rendered from a transcript, not a screen capture**, and the report stated that. Real screen captures: VM console `VBoxManage controlvm <vm> screenshotpng f.png`; web pages `chrome --headless=new --screenshot=f.png --window-size=1100,640 <url>`.
- Host screen capture (`screencapture`) needs the user to grant Screen Recording permission to the terminal/app. If it is not granted, the methods above replace it, or the user takes those shots.

## What worked

- A state-changing command ran once, in its final form; its syntax was tested separately first, and it was never piped into `head`.
- When something was done without a recorded output (a silent command), the report said so instead of implying a figure exists.
- Output was checked before use: old pods in a list, duplicate figures (`md5 a.png b.png`), a figure that does not prove its caption (for example a "via proxy" screenshot taken on a different port).
- The prompt in an image matched where the command really ran (working directory).
- Tall screenshots were split by lines or commands kept short, so each figure fit one page, and the final document was checked for overlaps with page numbers and margins.
- A timestamped problem log (time, type, what happened, cause, fix) included failures as well as successes.
- Web UIs behind a login form (such as Adminer) were screenshotted through a real login in headless Chrome (DevTools protocol), not through a faked request.
- Hand-drawn or code-drawn diagrams were labeled as diagrams, not screenshots.
