FROM python:3.6-stretch

RUN apt update && apt install -y \
#    ca-certificates \
#    g++ \
#    gcc \
    gdb \
    libseccomp-dev \
    linux-headers-amd64 \
    && true

COPY setup.py /setup.py
RUN python setup.py develop

ENV TURINGARENA_PROBLEMS_PATH /problems

ENTRYPOINT ["turingarena"]

COPY turingarena/ /turingarena/
