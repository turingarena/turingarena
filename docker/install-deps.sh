set -xe

apk add --no-cache \
    python3 \
    python3-dev \
    gcc \
    g++ \
    gdb \
    git \
    jq \
    linux-vanilla-dev \
    libseccomp-dev \
    nodejs \
    openjdk8 \
    openssh \
    socat \
    libxml2-dev \
    libxslt-dev \
    make \

cd /tmp

pip3 install -r /tmp/requirements.txt
