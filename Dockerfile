FROM turingarena/turingarena-base

COPY . /usr/local/turingarena/
RUN true \
    && cd /usr/local/turingarena/ \
    && python setup.py develop \
    && turingarena pythonsite \
    && turingarena install examples \
    && mkdir /problems \
    && turingarena install /problems \
    && true

ENTRYPOINT ["turingarena"]
WORKDIR /problems
