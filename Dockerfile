FROM python:3.6-stretch

RUN apt-get update && apt-get install -y \
#    ca-certificates \
#    g++ \
#    gcc \
    openjdk-8-jdk \
    gdb \
    libseccomp-dev \
    linux-headers-amd64 \
    nodejs \
    && true

COPY setup.py /setup.py
RUN python setup.py develop

ENTRYPOINT ["turingarena"]

COPY turingarena/ /turingarena/
COPY examples/ /examples/

RUN true \
    && turingarena pythonsite \
    && turingarena install /examples \
    && mkdir /problems \
    && turingarena install /problems \
    && true
