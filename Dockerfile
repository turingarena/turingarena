FROM python:3.6-stretch

RUN apt update && apt install -y \
    ca-certificates \
    g++ \
    gcc \
    gdb \
    libseccomp-dev \
    linux-headers-amd64 \
    && true

RUN \
    ln -sf pip3 /usr/bin/pip && \
    ln -sf python3 /usr/bin/python && \
    true

COPY setup.py /setup.py

RUN python setup.py develop

ENTRYPOINT ["turingarena"]

COPY turingarena/ /turingarena/
COPY test_challenge/ /test_challenge/
