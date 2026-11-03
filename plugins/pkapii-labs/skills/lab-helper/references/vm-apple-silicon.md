# Linux VM in VirtualBox on Apple Silicon (tested: VirtualBox 7.2.20, Ubuntu 22.04.5 ARM64)

Variables used below: `VM=lab-vm`, `NAT=lab-nat`, `GUEST_USER=<user>`. Run from a working folder such as `vm/`.

## Facts that save hours

- VirtualBox on M-series runs only ARM guests. Take `ubuntu-22.04.5-live-server-arm64.iso`, not amd64 (cdimage.ubuntu.com). Verify the SHA256 from `SHA256SUMS` on the same site. Download in the background with `curl -sL -C -` (resumable), about 2 GB.
- The default graphics (`vboxvga`) fails with `VERR_PGM_RAM_CONFLICT`. Use `--graphicscontroller=vmsvga`.
- Use exactly one storage controller, VirtIO SCSI. SATA together with it conflicts on MMIO (see `VBox.log`).
- The installer and the installed system show a black screen and the CPU idles unless the kernel gets `modprobe.blacklist=vmwgfx modules_load=simplefb`. The guest hangs on the vmwgfx driver, and without `simplefb` the console is not drawn. Changing the NIC type or adding `nomodeset` did not help.
- A manual installer wizard is unreliable here. Use `VBoxManage unattended` and patch the files it generates.
- `VBoxManage modifynvram <vm> listvars` crashes in 7.2.20. Use only `inituefivarstore` to reset stale EFI boot entries.
- Debugging blind: write the serial port to a file and grep it. The guest console is also available as PNG: `VBoxManage controlvm $VM screenshotpng file.png`.

## Create the VM

```bash
VM=lab-vm; NAT=lab-nat
VBoxManage natnetwork add --netname $NAT --network "10.0.2.0/24" --enable --dhcp on
VBoxManage createvm --name=$VM --platform-architecture=arm --ostype=Ubuntu22_arm64 --basefolder="$PWD/vms" --register
VBoxManage modifyvm $VM --cpus=1 --memory=2048 --graphicscontroller=vmsvga --vram=32 \
  --usb-xhci=on --keyboard=usb --mouse=usbtablet --nic1=natnetwork --nat-network1=$NAT
VBoxManage createmedium disk --filename "$PWD/vms/$VM/$VM.vdi" --size 25600 --format VDI
VBoxManage storagectl $VM --name VirtioSCSI --add virtio-scsi --controller VirtioSCSI --bootable on
VBoxManage storageattach $VM --storagectl VirtioSCSI --port 0 --device 0 --type hdd --medium "$PWD/vms/$VM/$VM.vdi"
VBoxManage unattended install $VM --iso="$PWD/ubuntu-22.04.5-live-server-arm64.iso" \
  --user=<user> --password=<password> --full-user-name="<name>" --hostname=<host>.local \
  --locale=en_US --time-zone=Europe/Moscow            # no --start-vm yet
```

Use the resource sizes your assignment says. Kubernetes labs with a multi-node kind cluster need 2 CPUs and 4 GB (resize later: shut down, `modifyvm --cpus 2 --memory 4096`, start).

`unattended install` puts the installer media on port 0 and may move the disk. Make sure the disk ends up on port 1 afterwards:
`VBoxManage storageattach $VM --storagectl VirtioSCSI --port 1 --device 0 --type hdd --medium <vdi> --nonrotational on --discard on`.

## Patch the generated installer files

In `vms/$VM/` the command creates `Unattended-<uuid>-grub.cfg`, `-user-data`, `-vboxpostinstall.sh`, `-aux-iso.viso`. Keep `.orig` copies, then:

1. In `grub.cfg`, append to every `linux` line: `earlycon console=ttyAMA0,115200 console=tty0 modprobe.blacklist=vmwgfx modules_load=simplefb`, and set `set timeout=15`.
2. Create an SSH key: `ssh-keygen -t ed25519 -N '' -C lab -f vm/id_lab -q`.
3. Replace `user-data` (keep the password hash that was generated, or make one with `openssl passwd -6`):

```yaml
#cloud-config
autoinstall:
  version: 1
  apt:
    fallback: offline-install
  locale: en_US.UTF-8
  keyboard:
    layout: us
  shutdown: reboot
  storage:
    layout:
      name: direct
    swap:
      size: 0
  identity:
    hostname: '<host>'
    username: '<user>'
    realname: '<name>'
    password: '<PASSWORD_HASH>'
  ssh:
    install-server: true
    allow-pw: true
    authorized-keys:
      - '<contents of vm/id_lab.pub>'
  user-data:
    timezone: Etc/UTC
  late-commands:
    - cp /cdrom/vboxpostinstall.sh /target/root/vboxpostinstall.sh
    - chmod +x /target/root/vboxpostinstall.sh
    - curtin in-target --target=/target -- /bin/bash /root/vboxpostinstall.sh --direct
    - echo 'blacklist vmwgfx' > /target/etc/modprobe.d/blacklist-vmwgfx.conf
    - sed -i 's/^GRUB_CMDLINE_LINUX_DEFAULT=.*/GRUB_CMDLINE_LINUX_DEFAULT="modprobe.blacklist=vmwgfx console=ttyAMA0,115200 console=tty0 modules_load=simplefb"/' /target/etc/default/grub
    - echo simplefb >> /target/etc/initramfs-tools/modules
    - curtin in-target --target=/target -- update-grub
    - curtin in-target --target=/target -- update-initramfs -u
```

## Install and wait

```bash
VBoxManage modifyvm $VM --uart1 0x3F8 4 --uart-mode1 file "$PWD/vms/$VM/serial.log"   # optional, for diagnosis
VBoxManage modifynvram $VM inituefivarstore
VBoxManage startvm $VM --type headless
until grep -aq "<host> login:" vms/$VM/serial.log; do sleep 5; done                  # about 10 minutes
```

The installer reboots by itself; the DVD is empty afterwards. If an attempt fails, poweroff, delete and recreate the disk (`closemedium disk ... --delete`, `createmedium`), reattach, and retry. A clean retry is faster than repairing.

## Network and access

```bash
VBoxManage dhcpserver modify --network=$NAT --vm=$VM --nic=1 --fixed-address=10.0.2.3
VBoxManage natnetwork modify --netname $NAT --port-forward-4 'ssh:tcp:[127.0.0.1]:2222:[10.0.2.3]:22'
VBoxManage natnetwork modify --netname $NAT --port-forward-4 'web:tcp:[]:8080:[10.0.2.3]:8080'
```

Add one forward per host port the labs publish (for example 8080 for web apps, 30000 for a Kubernetes NodePort). The guest interface is `enp0s8`. SSH: `ssh -i vm/id_lab -p 2222 -o IdentitiesOnly=yes <user>@127.0.0.1`. The host key changes on every reinstall: use a throwaway `known_hosts` or `StrictHostKeyChecking no` for this VM only.

For scripted work, enable passwordless sudo **inside the lab VM only**:
`echo '<password>' | sudo -S sh -c 'echo "<user> ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/90-lab && chmod 440 /etc/sudoers.d/90-lab'`.

Wrap `VBoxManage` in a small script that appends each command and its output to a log file; the log doubles as evidence for the assignment.

## Clean up (only when the user asks)

```bash
VBoxManage controlvm $VM acpipowerbutton           # graceful; wait about a minute; "acpipoweroff" does not exist
VBoxManage unregistervm $VM --delete               # removes registration, disk and VM files
VBoxManage natnetwork remove --netname $NAT
VBoxManage dhcpserver remove --network=$NAT        # leftover DHCP server of that NAT network
```

`unregistervm --delete` leaves the generated installer files and serial logs in the VM folder; save what you need, then remove the folder. Do not touch host-only networks you did not create. The ISO and SSH key can stay for a rerun.
