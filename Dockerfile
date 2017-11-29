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
    && true

RUN \
    ln -sf pip3 /usr/bin/pip && \
    ln -sf python3 /usr/bin/python && \
    true

COPY setup.py setup.py
RUN python setup.py develop

RUN \
    sed -i s/#PermitRootLogin.*/PermitRootLogin\ yes/ /etc/ssh/sshd_config && \
    echo "root:root" | chpasswd && \
    true

RUN ssh-keygen -A

# do not detach (-D), log to stderr (-e)
CMD ["/usr/sbin/sshd", "-D", "-e"]

COPY turingarena/ turingarena/
