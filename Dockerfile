ARG BASE_IMAGE=turingarena/turingarena-base
FROM $BASE_IMAGE

COPY . /usr/local/turingarena/
RUN true \
    && ssh-keygen -A \
    && ln -sf /usr/bin/python3 /usr/local/bin/python \
    && ln -s /usr/lib/jvm/default-jvm/bin/javac /usr/local/bin/javac \
    && ln -s /usr/lib/jvm/default-jvm/bin/jcmd /usr/local/bin/jcmd \
    && cd /usr/local/turingarena/ \
    && python setup.py develop \
    && python -m turingarena_impl.cli.main pythonsite \
    && python -m turingarena_impl.cli.main install examples \
    && true

ENTRYPOINT ["turingarena"]
WORKDIR /problems
