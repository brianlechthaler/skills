# Cloud-Init Examples

Replace SSH public keys, hostnames, and image IDs before launch. Templates assume first-boot `#cloud-config`.

## Ubuntu 24.04 LTS — baseline SSH + updates

```yaml
#cloud-config
hostname: app-1
manage_etc_hosts: true
timezone: Etc/UTC

users:
  - default
  - name: deploy
    groups: [sudo, docker]
    shell: /bin/bash
    sudo: ALL=(ALL) NOPASSWD:ALL
    ssh_authorized_keys:
      - ssh-ed25519 AAAA...REPLACE_WITH_YOUR_KEY

ssh_pwauth: false
package_update: true
package_upgrade: true

packages:
  - ca-certificates
  - curl
  - fail2ban
  - unattended-upgrades

runcmd:
  - systemctl enable --now fail2ban
```

## Ubuntu 24.04 — Docker Compose app

Installs Docker Engine + Compose plugin, writes compose files, starts the stack.

```yaml
#cloud-config
hostname: web-1
users:
  - default
  - name: deploy
    groups: [sudo, docker]
    shell: /bin/bash
    sudo: ALL=(ALL) NOPASSWD:ALL
    ssh_authorized_keys:
      - ssh-ed25519 AAAA...REPLACE_WITH_YOUR_KEY

ssh_pwauth: false
package_update: true

packages:
  - ca-certificates
  - curl

write_files:
  - path: /opt/app/compose.yaml
    owner: root:root
    permissions: "0644"
    content: |
      services:
        app:
          image: nginx:1.27-alpine
          ports:
            - "80:80"
          restart: unless-stopped

runcmd:
  - install -m 0755 -d /etc/apt/keyrings
  - curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  - chmod a+r /etc/apt/keyrings/docker.asc
  - |
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" > /etc/apt/sources.list.d/docker.list
  - apt-get update -y
  - apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
  - usermod -aG docker deploy
  - cd /opt/app && docker compose up -d
```

Prefer copying a real project `compose.yaml` via `write_files` (or `scp` after boot). Keep the Docker apt codename dynamic as above.

## Debian 12 — nginx reverse proxy

```yaml
#cloud-config
hostname: edge-1
users:
  - default
  - name: deploy
    groups: [sudo]
    shell: /bin/bash
    sudo: ALL=(ALL) NOPASSWD:ALL
    ssh_authorized_keys:
      - ssh-ed25519 AAAA...REPLACE_WITH_YOUR_KEY

ssh_pwauth: false
package_update: true
packages:
  - nginx
  - certbot
  - python3-certbot-nginx

write_files:
  - path: /etc/nginx/sites-available/app
    permissions: "0644"
    content: |
      server {
          listen 80 default_server;
          server_name _;
          location / {
              proxy_pass http://127.0.0.1:3000;
              proxy_set_header Host $host;
              proxy_set_header X-Real-IP $remote_addr;
          }
      }

runcmd:
  - ln -sf /etc/nginx/sites-available/app /etc/nginx/sites-enabled/app
  - rm -f /etc/nginx/sites-enabled/default
  - nginx -t && systemctl reload nginx
```

## Rocky Linux 9 — dnf packages + firewalld

```yaml
#cloud-config
hostname: rocky-app-1
users:
  - name: deploy
    groups: [wheel]
    shell: /bin/bash
    sudo: ALL=(ALL) NOPASSWD:ALL
    ssh_authorized_keys:
      - ssh-ed25519 AAAA...REPLACE_WITH_YOUR_KEY

ssh_pwauth: false
package_update: true
packages:
  - nginx
  - firewalld
  - policycoreutils-python-utils

runcmd:
  - systemctl enable --now firewalld
  - firewall-cmd --permanent --add-service=http
  - firewall-cmd --permanent --add-service=https
  - firewall-cmd --reload
  - systemctl enable --now nginx
```

Keep SELinux Enforcing. For nonstandard ports, add `semanage port` rules in `runcmd` rather than disabling SELinux.

## Amazon Linux 2023 — SSM-friendly bootstrap

```yaml
#cloud-config
hostname: al2023-app-1
package_update: true
packages:
  - docker
  - nginx

users:
  - name: ec2-user
    groups: [docker]
    # Prefer instance SSH key from AWS or SSM Session Manager;
    # add ssh_authorized_keys only when not using cloud keypair/SSM.

runcmd:
  - systemctl enable --now docker
  - systemctl enable --now nginx
```

On AWS, prefer EC2 key pair or SSM Session Manager over shipping keys in user-data when possible. Still valid to include `ssh_authorized_keys` for automation outside AWS.

## NoCloud meta-data

`cloud-init/meta-data`:

```yaml
instance-id: iid-app-1
local-hostname: app-1
```

Minimal `network-config` (v2) DHCP example:

```yaml
version: 2
ethernets:
  eth0:
    dhcp4: true
```

Create seed image:

```bash
cloud-localds seed.img cloud-init/user-data cloud-init/meta-data
```

## Multipass launch

```bash
multipass launch 24.04 --name app --cloud-init cloud-init/user-data
multipass shell app
```

## Terraform (AWS example snippet)

```hcl
resource "aws_instance" "app" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.small"
  user_data     = file("${path.module}/cloud-init/user-data")

  tags = { Name = "app-1" }
}
```

Some providers require `user_data_base64 = base64gzip(file(...))` for size limits — check the provider docs.

## Systemd unit via write_files

```yaml
#cloud-config
packages:
  - python3

write_files:
  - path: /opt/app/app.py
    permissions: "0644"
    content: |
      #!/usr/bin/env python3
      from http.server import BaseHTTPRequestHandler, HTTPServer
      class H(BaseHTTPRequestHandler):
          def do_GET(self):
              self.send_response(200)
              self.end_headers()
              self.wfile.write(b"ok")
      HTTPServer(("", 8080), H).serve_forever()
  - path: /etc/systemd/system/app.service
    permissions: "0644"
    content: |
      [Unit]
      Description=App
      After=network-online.target
      [Service]
      ExecStart=/usr/bin/python3 /opt/app/app.py
      Restart=on-failure
      [Install]
      WantedBy=multi-user.target

runcmd:
  - systemctl daemon-reload
  - systemctl enable --now app.service
```
