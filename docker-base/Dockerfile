FROM alpine:3.7

RUN true \
    && apk add --no-cache \
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
        make \
    && pip3 install \
        bidict \
        boto3 \
        coloredlogs \
        commonmark \
        docopt \
        pbr \
        pyyaml \
        pytest-sugar \
        pytest-xdist \
        psutil \
        seccomplite \
        pytest \
        tatsu \
        toml \
        networkx \
    && wget https://ftp.gnu.org/gnu/glpk/glpk-4.65.tar.gz \
    && tar -xvf glpk-4.65.tar.gz \
    && cd glpk-4.65 \
    && ./configure --prefix=/usr \
    && make install \
    && cd .. \
    && rm -rf glpk-4.65.tar.gz glpk-4.65 \
    && true
