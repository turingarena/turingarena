FROM ubuntu

RUN true \
    && apt-get update \
    && apt-get install -y \
        jq \
        python3-pip \
        curl \
        gnupg \
    && curl -L https://hyper-install.s3.amazonaws.com/hyper-linux-x86_64.tar.gz -o - \
        | tar -zx -C /usr/local/bin \
    && curl -sL https://deb.nodesource.com/setup_10.x | bash - \
    && apt-get install -y \
        gcc \
        g++ \
        make \
        nodejs \
    && npm install -g \
        lerna \
        neutrino \
        serverless \
        surge \
        yarn \
    && pip3 install \
        setuptools \
        twine \
        wheel \
    && true
