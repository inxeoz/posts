# Setting Up Local *.test DNS Resolution Without Breaking System DNS

## Introduction

When developing with Frappe Manager, sites are typically created with domains ending in `.test` (e.g., `demo.test`). To access these locally, you need DNS resolution for `*.test` domains to point to `127.0.0.1`. However, this should not interfere with your system's existing DNS setup, especially if you're using VPNs like Cloudflare Warp that manage DNS.

This guide shows how to configure local DNS for `*.test` domains using `dnsmasq`, while forwarding all other queries to your system's upstream DNS (e.g., Warp's servers).

## Prerequisites

- Linux system (Arch Linux in this example, but adaptable to others)
- `pacman` package manager (or equivalent)
- Cloudflare Warp running (or any VPN that sets custom DNS)
- Root access

## Step 1: Install dnsmasq

Install `dnsmasq`, a lightweight DNS forwarder and DHCP server:

```bash
sudo pacman -S dnsmasq
```

## Step 2: Configure dnsmasq

Edit `/etc/dnsmasq.conf` to add the following lines (after the existing address example):

```conf
# Wildcard for .test domains
address=/.test/127.0.0.1

# Forward to upstream DNS (replace with your VPN's DNS servers)
server=127.0.2.2
server=127.0.2.3

# Listen on localhost only
listen-address=127.0.0.1
bind-interfaces
```

- `address=/.test/127.0.0.1`: Resolves all `.test` subdomains to `127.0.0.1`.
- `server=...`: Forwards non-matching queries to your upstream DNS (e.g., Warp's 127.0.2.2 and 127.0.2.3).
- `listen-address` and `bind-interfaces`: Restricts dnsmasq to localhost for security.

## Step 3: Configure systemd-resolved

Edit `/etc/systemd/resolved.conf` to set dnsmasq as the primary DNS:

```conf
[Resolve]
DNS=127.0.0.1
DNSStubListener=no
```

- `DNS=127.0.0.1`: Points systemd-resolved to dnsmasq.
- `DNSStubListener=no`: Disables the local stub resolver to avoid conflicts.

Restart systemd-resolved:

```bash
sudo systemctl restart systemd-resolved
```

## Step 4: Start dnsmasq

Enable and start the dnsmasq service:

```bash
sudo systemctl enable dnsmasq
sudo systemctl start dnsmasq
```

## Verification

Test the setup:

- For `.test` domains: `dig demo.test` should return `127.0.0.1`.
- For other domains: `dig google.com` should resolve normally via your upstream DNS.

Access your Frappe sites at `http://demo.test` in your browser.

## How It Works

- Queries for `*.test` are answered directly by dnsmasq with `127.0.0.1`.
- All other queries are forwarded to your VPN's DNS servers.
- systemd-resolved acts as a bridge, ensuring compatibility with system services.
- Your VPN (e.g., Warp) continues to handle external DNS without interruption.

## Troubleshooting

- If DNS doesn't work, check `/var/log/syslog` or `journalctl -u dnsmasq` for errors.
- Ensure no other DNS services (e.g., unbound) are conflicting on port 53.
- For IPv6 issues, add `bind-interfaces` and ensure IPv6 is handled if needed.

## Reverting Changes

To undo:

1. Stop and remove dnsmasq: `sudo systemctl stop dnsmasq && sudo pacman -R dnsmasq`
2. Revert `/etc/systemd/resolved.conf` to defaults.
3. Restart systemd-resolved: `sudo systemctl restart systemd-resolved`

This setup keeps your system DNS intact while providing local resolution for development.
