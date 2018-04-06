FROM turingarena/turingarena-base

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
