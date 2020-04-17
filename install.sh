#!/bin/bash
# Install or update TuringArena on a server

msg() {
    echo "==> $@"
}

gen_secret() {
    head -c42 /dev/urandom | base64
}

PORT="3000"
HOST="localhost"

REPO="${PWD}"
BIN="${HOME}/.local/bin/turingarena"
DEST="${HOME}/.local/share/turingarena"
CONFIG="${HOME}/.config/turingarena/turingarena.conf.json"
CACHE="${HOME}/.cache/turingarena"

msg "Create directories"
mkdir -p "${DEST}/backend"
mkdir -p "${DEST}/frontend"
mkdir -p "${CACHE}"
mkdir -p "${HOME}/.local/bin"
mkdir -p "${HOME}/.config/turingarena"

msg "Build backend"
cd "${REPO}/server/"
npm ci

msg "Install backend"
cp -r * "${DEST}/backend"

msg "Build client"
cd "${REPO}/web/"
npm ci

msg "Install client"
cp -r build "${DEST}/frontend"

msg "Install binary ${BIN}"
tee "${BIN}" << EOF
#!/bin/sh

NODE_PATH="${DEST}/backend/node_modules/" exec node "${DEST}/backend/dist/src/cli/index.js" --config "${CONFIG}" "\$@"
EOF
chmod +x "${BIN}"

msg "Create config file in ${CONFIG}"
tee "${CONFIG}" <<EOF
{
    "db": {
        "storage": "${DEST}/db.sqlite3",
        "dialect": "sqlite"
    },
    "host": "${HOST}",
    "port": ${PORT},
    "secret": "$(gen_secret)",
    "skipAuth": false,
    "cachePath": "${CACHE}",
    "webRoot": "${DEST}/frontend"
}
EOF

if [ "$(uname)" = "Linux" ]; then
    msg "You may want to copy this systemd unit file"
    cat <<EOF
[Unit]
Description=turingarena server

[Service]
User=${USER}
Group=${USER}
Type=simple
WorkingDirectory=${DEST}/backend
Restart=always
ExecStart=node ${DEST}/backend/dist/scripts/serve.js

[Install]
WantedBy=multi-user.target
EOF
    msg "Put it in /etc/systemd/system/turingarena.service or your home directory"
fi
