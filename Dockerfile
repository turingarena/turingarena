FROM alpine:3.6

RUN apk add --no-cache \
    ca-certificates \
    cmake \
    g++ \
    gcc \
    git \
    make \
    openssh \
    python3 \
    socat \
    && true

RUN \
    ln -sf pip3 /usr/bin/pip && \
    ln -sf python3 /usr/bin/python && \
    true

COPY setup.py /setup.py
RUN python setup.py develop

RUN ssh-keygen -A

WORKDIR /root
RUN mkdir db.git && git init --bare db.git

ENTRYPOINT ["turingarena"]

COPY turingarena/ /turingarena/
