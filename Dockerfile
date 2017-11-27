FROM debian:buster
RUN \
    apt-get update && \
    apt-get -y install \
    build-essential \
    python3.6-dev \
    python3-pip \
    openssh-server \
    ""

RUN ln -s /usr/bin/python3 /usr/local/bin/python
RUN ln -s /usr/bin/pip3 /usr/local/bin/pip

COPY setup.py setup.py
RUN python setup.py develop

COPY turingarena/ turingarena/
