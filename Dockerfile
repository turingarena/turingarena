FROM python:3.6-stretch

RUN apt-get update && apt-get install -y \
#    ca-certificates \
#    g++ \
#    gcc \
    openjdk-8-jdk \
    gdb \
    libseccomp-dev \
    linux-headers-amd64 \
    && true

COPY setup.py /setup.py
RUN python setup.py develop

ENV TURINGARENA_PROBLEMS_PATH /problems

ENTRYPOINT ["turingarena"]

COPY turingarena/ /turingarena/
COPY examples/ /problems/
