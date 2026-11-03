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
- The image is **rendered from a transcript, not a screen capture.** Say so in the report. Real screen captures: VM console `VBoxManage controlvm <vm> screenshotpng f.png`; web pages `chrome --headless=new --screenshot=f.png --window-size=1100,640 <url>`.
- Host screen capture (`screencapture`) needs the user to grant Screen Recording permission to the terminal/app. If it is not granted, do not work around it; use the methods above or ask the user to take those shots.

## Rules

- A command that changes state is run once with its final form. Test syntax separately first; do not pipe it into `head`.
- If something was done without a recorded output (a silent command), the report must say it, not imply a figure exists.
- Check the output before using it: old pods in a list, duplicate figures (`md5 a.png b.png`), a figure that does not prove its caption (for example a "via proxy" screenshot taken on a different port).
- Keep prompts honest: the working directory shown must match where the command ran.
- Tall screenshots: split by lines or keep commands short, so each figure fits one page. Check that nothing overlaps page numbers or margins in the final document, whatever tool produced it.
- Keep a timestamped problem log (time, type, what happened, cause, fix). Log failures too; they are useful and honest.
- Web UIs behind a login form (such as Adminer): automate a real login through headless Chrome (DevTools protocol) instead of faking a request.
- Diagrams drawn by hand or code are not screenshots; label them as diagrams.
