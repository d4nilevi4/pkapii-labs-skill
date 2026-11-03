# How the agent worked with the VM

Practical routine from the original run: how access was set up, how commands were executed, how screenshots were made. Placeholders: `<user>`, `<password>`, `<host>`, `<vm>`.

## Access

- **User.** Created by the autoinstall `identity` block (see `vm-apple-silicon.md`): username, hostname and password chosen by the student. If the assignment names no team or variant number, a plain username of the student's choice is enough.
- **SSH key.** One dedicated ed25519 key without passphrase for this VM only (`ssh-keygen -t ed25519 -N '' -C lab -f vm/id_lab -q`). The public key goes into `authorized-keys` of the autoinstall file, so the first boot already accepts it. Password login stays enabled as a fallback.
- **Route.** A NAT-network port forward `127.0.0.1:2222 -> guest:22` (`vm-apple-silicon.md`). Options for this throwaway VM: `-i vm/id_lab -p 2222 -o IdentitiesOnly=yes -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR`. The host key changes after every reinstall, hence the throwaway `known_hosts`.
- **sudo.** Passwordless sudo inside the VM only, through `/etc/sudoers.d/90-lab` with `<user> ALL=(ALL) NOPASSWD:ALL` and mode 440, created once over SSH with the password. Scripted `sudo` calls then never wait for input.
- **Resources.** Raised later by powering the VM off from inside (`sudo poweroff`), `VBoxManage modifyvm <vm> --cpus 2 --memory 4096`, starting headless and waiting until SSH answers (`until ssh ... true; do sleep 5; done`).
- **Headless.** The VM ran with `VBoxManage startvm <vm> --type headless`; nothing needed a VM window.

## Running commands

All commands went through `scripts/vmrun.py`:

```bash
export LAB_SSH_USER=<user> LAB_SSH_KEY=vm/id_lab LAB_SSH_PORT=2222 LAB_OUT=evidence
python3 scripts/vmrun.py lab3_07_up --cwd '~/project' "docker compose up -d --build 2>&1 | tail -22" "docker compose ps"
```

- Every command opens its own SSH session and runs as `bash -lc 'exec 2>&1; cd <dir> && <command>'`. A login shell gives the normal `PATH`; a fresh session picks up a new group membership (for example `docker` right after `usermod -aG`). `exec 2>&1` puts stderr and stdout in the order a terminal shows.
- Several commands in one call share one screenshot; each is printed as `<user>@vm:<dir>$ command` followed by its output, and a failing command does not stop the next one.
- Files were created inside the VM with a heredoc as an ordinary command, followed by `cat` of the file, so the transcript shows the file and the check:
  `"cat > app.yaml <<'EOF'\n...\nEOF" "cat app.yaml"` (the quoted `'EOF'` stops the shell from expanding `$` and backticks).
- Waiting was explicit: `kubectl wait --for=condition=Ready pod -l app=x --timeout=120s`, `sleep 30; kubectl get pods`, or `until <check>; do sleep 5; done`. The script allows 30 minutes per command.
- Interactive programs were avoided: `psql -c`, `-P pager=off`, `docker exec` without `-it` (`--tty` exists for the rare case that needs a pseudo-terminal).
- Commands for the Mac itself (`VBoxManage`, `curl` to a forwarded port) used `--host`; the prompt then reads `student@host`. Testing a published port with `curl` from the host shows the whole path through the NAT forward.
- Between labs the previous lab's objects were removed (stack, cluster), as the assignments require; this was logged.

## Screenshots

1. **Terminal figures.** `termshot.py` draws a dark terminal window (Menlo 15, 112 columns, coloured prompt) from the transcript text. One `vmrun.py` call produces `<name>.txt` and `<name>.png`. Emoji are dropped in the image only. An image is 1036 px wide; very tall output was split into parts that each fit a page.
2. **VM console.** `VBoxManage controlvm <vm> screenshotpng file.png`, used for the installer, boot and login screens. A loop with `sleep 4` between shots catches the stages of a long install.
3. **Web pages.** `scripts/browsershot.sh out.png URL [W H]` for plain pages. For a login form, `scripts/adminer_login.mjs` starts headless Chrome with a remote-debugging port, connects over a WebSocket (Node 22+), submits the real form, optionally opens a second path and saves `Page.captureScreenshot`. `BASE=http://127.0.0.1:<port>/` picks the forwarded host port, which is how "through the proxy" shots were taken.
4. **Diagrams.** Drawn with Pillow when the assignment asks for a scheme; labeled as a diagram.

Host screen capture (`screencapture`) was not available (no Screen Recording permission), which is why terminal figures are rendered from real output.

## Records

- Names like `<lab>_<nn>_<topic>` for both `.png` and `.txt`.
- A wrapper for `VBoxManage` that appends the command and its output to one log file.
- A timestamped problem log: time, type (ok, problem, decision, info), what happened.
- Before use, each image was opened and compared with its caption.
