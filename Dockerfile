ARG BASE_IMAGE=turingarena/turingarena-base
FROM $BASE_IMAGE

ENV TURINGARENA_PATH_FILE=/usr/lib/python3.6/site-packages/turingarena.pth

COPY . /usr/local/turingarena/

RUN true \
    && ssh-keygen -A \
    && echo 'turingarena:x:1000:1000::/run/turingarena:/bin/ash' >> /etc/passwd \
    && passwd -d turingarena \
    && ln -sf /usr/bin/python3 /usr/local/bin/python \
    && ln -s /usr/lib/jvm/default-jvm/bin/javac /usr/local/bin/javac \
    && ln -s /usr/lib/jvm/default-jvm/bin/jcmd /usr/local/bin/jcmd \
    && cd /usr/local/turingarena/ \
    && python turingarena_impl/setup.py develop \
    && echo '/usr/local/turingarena/examples' >> $TURINGARENA_PATH_FILE \
    && true
