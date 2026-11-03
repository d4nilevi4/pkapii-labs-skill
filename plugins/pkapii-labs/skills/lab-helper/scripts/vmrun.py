"""Run commands in the lab VM over SSH (or on the host with --host), keep the REAL transcript, render a terminal screenshot.
  python3 vmrun.py SHOT [--host] [--tty] [--cwd DIR] "cmd1" "cmd2" ...
Output: <out>/SHOT.txt (transcript) and <out>/SHOT.png (rendered from that transcript, not a screen capture).
Settings by environment: LAB_SSH_USER (required for VM mode), LAB_SSH_KEY (default ~/.ssh/id_ed25519),
LAB_SSH_HOST (127.0.0.1), LAB_SSH_PORT (2222), LAB_OUT (./evidence).
Each command runs separately in a login shell with stderr merged into stdout, so the order matches a real terminal.
Say in your report that images are rendered from transcripts."""
import argparse, os, shlex, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from termshot import render

USER = os.environ.get("LAB_SSH_USER", "")
KEY = os.path.expanduser(os.environ.get("LAB_SSH_KEY", "~/.ssh/id_ed25519"))
HOST = os.environ.get("LAB_SSH_HOST", "127.0.0.1")
PORT = os.environ.get("LAB_SSH_PORT", "2222")
OUT = os.environ.get("LAB_OUT", "evidence")

def run_host(cmd, cwd):
    p = subprocess.run(["/bin/zsh", "-c", cmd], cwd=cwd or None, capture_output=True, text=True, timeout=1800)
    return (p.stdout + p.stderr).rstrip("\n")

def run_vm(cmd, cwd, tty):
    ssh = ["ssh", "-i", KEY, "-p", PORT, "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
           "-o", "LogLevel=ERROR", "-o", "IdentitiesOnly=yes"] + (["-tt"] if tty else []) + [f"{USER}@{HOST}"]
    remote = "exec 2>&1; " + (f"cd {cwd} && {cmd}" if cwd else cmd)
    p = subprocess.run(ssh + ["bash -lc " + shlex.quote(remote)], capture_output=True, text=True, timeout=1800)
    return (p.stdout + p.stderr).rstrip("\n")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("shot"); ap.add_argument("--tty", action="store_true"); ap.add_argument("--cwd", default="")
    ap.add_argument("--host", action="store_true", help="run on the host instead of the VM")
    ap.add_argument("cmds", nargs="+")
    a = ap.parse_args()
    if not a.host and not USER:
        sys.exit("set LAB_SSH_USER (and LAB_SSH_KEY/LAB_SSH_PORT if needed) or use --host")
    who = "student@host" if a.host else f"{USER}@vm"
    shown = a.cwd or "~"
    parts = []
    for c in a.cmds:
        out = run_host(c, a.cwd) if a.host else run_vm(c, a.cwd, a.tty)
        parts.append(f"{who}:{shown}$ {c}" + ("\n" + out if out else ""))
    text = "\n".join(parts)
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, a.shot + ".txt"), "w").write(text + "\n")
    render(text, os.path.join(OUT, a.shot + ".png"), f"{who}: {shown}")
    print(text)
