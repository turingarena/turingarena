ARG BASE_IMAGE=turingarena/turingarena-base
FROM $BASE_IMAGE

ENTRYPOINT []
ENV GIT_DIR=/run/turingarena/db.git

COPY . /usr/local/turingarena/

RUN true \
    && ssh-keygen -A \
    && echo 'turingarena:x:1000:1000::/run/turingarena:/bin/ash' >> /etc/passwd \
    && passwd -d turingarena \
    && ln -sf /usr/bin/python3 /usr/local/bin/python \
    && ln -s /usr/lib/jvm/default-jvm/bin/javac /usr/bin/javac \
    && ln -s /usr/lib/jvm/default-jvm/bin/jcmd /usr/bin/jcmd \
    && cd /usr/local/turingarena/backend/ && python setup.py develop \
    && cd /usr/local/turingarena/libraries/python3/ && python setup.py develop \
    && mkdir -p /usr/local/include/\
    && cp /usr/local/turingarena/libraries/cpp/turingarena.h /usr/local/include/ \
    && mkdir /run/turingarena \
    && true
