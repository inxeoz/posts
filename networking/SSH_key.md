---
title: Complete GitHub SSH Setup Guide for Linux Developers
date: '2026-01-27'
description: SSH keys provide secure, passwordless authentication to GitHub repositories
  with complete setup guide
permalink: posts/{{ title | slug }}/index.html
tags:
- ssh
- github
- linux
- security
- authentication
categories:
- networking
---

# Complete GitHub SSH Setup Guide for Linux Developers

SSH keys provide secure, passwordless authentication to GitHub repositories. This guide covers every step from enabling SSH to testing the connection, tailored for Arch Linux/Manjaro users with i3/Hyprland window managers.

## SSH Key Concepts
SSH uses public-key cryptography with a private key (stays on your machine) and public key (shared with GitHub). The private key never leaves your system; GitHub verifies your identity by checking your public key signature.[1][7]

## Step 1: Check Existing Keys
List SSH keys in your `.ssh` directory:
```
ls -al ~/.ssh
```
Look for pairs like `id_ed25519` (private) and `id_ed25519.pub` (public), or `id_rsa`/`id_rsa.pub`. Skip to Step 3 if they exist and work.[4]

## Step 2: Generate New SSH Key Pair
Use Ed25519 (modern, secure) for your GitHub email:
```
ssh-keygen -t ed25519 -C "your-github-email@example.com"
```
- Press Enter for default location (`~/.ssh/id_ed25519`)
- Enter passphrase twice (recommended for security) or leave blank
- Creates `id_ed25519` (private) and `id_ed25519.pub` (public)

Set correct permissions:
```
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
```

## Step 3: Start SSH Agent Properly
Your earlier issue occurred because `ssh-agent` output wasn't evaluated. Run:
```
eval "$(ssh-agent -s)"
```
Output shows `SSH_AUTH_SOCK` and `SSH_AGENT_PID`. Now add your key:
```
ssh-add ~/.ssh/id_ed25519
```
Verify: `ssh-add -l` lists your loaded key fingerprint.

## Step 4: Permanent Agent Setup (Arch Linux)
Enable systemd user service for persistent agent across sessions:
```
systemctl --user enable --now ssh-agent
```
Add to `~/.bashrc` or `~/.zshrc`:
```
export SSH_AUTH_SOCK="$(ss -xl | grep -o '/run/user/[0-9]*/keyring/ssh$')"
```
Reload: `source ~/.bashrc`.[11]

## Step 5: Copy Public Key to GitHub
Display public key:
```
cat ~/.ssh/id_ed25519.pub
```
Copy entire output (starts with `ssh-ed25519`).

**GitHub Steps:**
1. Login → Settings → SSH and GPG keys
2. "New SSH key" → Title: "Arch Linux Main" → Paste key → Add SSH key

## Step 6: Test Connection
```
ssh -T git@github.com
```
**Success:** `Hi inxeoz! You've successfully authenticated, but GitHub does not provide shell access.`
**Verbose debug:** `ssh -Tvvv git@github.com` shows key negotiation details.[7][1]

## Common Configuration File
Create/edit `~/.ssh/config` for multiple GitHub accounts:
```
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes
```

## Troubleshooting Table

| Error | Cause | Fix |
|-------|-------|-----|
| `Permission denied (publickey)` | Key not in GitHub | Add public key to GitHub settings [5] |
| `Could not open connection to agent` | Agent not sourced | `eval "$(ssh-agent -s)"` then `ssh-add` [12] |
| `ssh: connect to host github.com port 22: Connection refused` | Firewall/proxy | Check `ss -tuln \| grep 22`, test `nc -zv github.com 22` |
| Multiple keys offered | Wrong config | Add `IdentitiesOnly yes` to `~/.ssh/config` [13] |

## Arch-Specific Notes
- **i3/Hyprland:** Agent persists via systemd; no PAM issues like GNOME.
- **Docker:** Mount agent socket: `-v $SSH_AUTH_SOCK:/agent.sock -e SSH_AUTH_SOCK=/agent.sock`.
- **Cloudflare Warp:** Ensure `warp-cli disconnect` during SSH setup if routing interferes.

