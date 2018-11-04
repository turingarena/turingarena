FROM alpine:3.7

COPY docker/install-deps.sh src/requirements.txt /tmp/

RUN sh /tmp/install-deps.sh
