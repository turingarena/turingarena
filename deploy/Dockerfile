ARG TURINGARENA_IMAGE=turingarena/turingarena
FROM $TURINGARENA_IMAGE as src

FROM alpine:3.7

RUN true \
    && apk add --no-cache \
        jq \
        nodejs \
        python3 \
    && wget https://hyper-install.s3.amazonaws.com/hyper-linux-x86_64.tar.gz \
    && tar -z -f hyper-linux-x86_64.tar.gz -x hyper -C /usr/local/bin \
    && rm hyper-linux-x86_64.tar.gz \
    && mkdir /lib64 \
    && ln -s /lib/ld-musl-x86_64.so.1 /lib64/ld-linux-x86-64.so.2 \
    && npm install -g serverless \
    && pip3 install \
        setuptools \
        twine \
        wheel \
    && true

COPY --from=src /usr/local/turingarena/ /src/
COPY deploy.sh deploy.sh

CMD sh deploy.sh
