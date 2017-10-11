FROM debian:buster
RUN \
    apt-get update && \
    apt-get -y install \
    build-essential \
    python3.6-dev \
    python3-pip \
    virtualenvwrapper \
    ""

WORKDIR /turingarena-workdir
RUN source /usr/share/virtualenvwrapper/virtualenvwrapper.sh
RUN mkvirtualenv -p $(which python3.6) turingarena
RUN pip install gunicorn
COPY setup.py setup.py
RUN python setup.py develop
COPY turingarena/ turingarena/
