sudo rpm --import https://pkgs.galtea.ai/public.key

sudo tee /etc/yum.repos.d/galtea.repo <<'EOF'
[galtea]
name=Galtea CLI
baseurl=https://pkgs.galtea.ai/yum
enabled=1
gpgcheck=1
gpgkey=https://pkgs.galtea.ai/public.key
EOF

sudo dnf install galtea
