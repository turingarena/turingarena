DESTDIR ?= /
PREFIX ?= /usr/local
DATA := ${DESTDIR}/${PREFIX}/share/turingarena/
BINDIR := ${DESTDIR}/${PREFIX}/bin
EXE := ${BINDIR}/turingarena

NPM ?= npm

WEB := web-react/
WEB_DEPS := ${WEB}/node_modules/
WEB_DIST := ${WEB}/build/
WEB_SRCS := ${WEB}/src/

SERVER := server/
SERVER_DEPS := ${SERVER}/node_modules/
SERVER_BUNDLE := ${SERVER}/dist/bundle.js
SERVER_SRCS := ${SERVER}/src/

all: ${SERVER_BUNDLE} ${WEB_DIST}

${WEB_DEPS}: ${WEB}/package-lock.json
	@echo "==> Install frontend deps"
	${NPM} --prefix ${WEB} ci

${SERVER_DEPS}: server/package-lock.json
	@echo "==> Install backend deps"
	${NPM} --prefix ${SERVER} ci

${WEB_DIST}: ${WEB_DEPS} ${WEB_SRCS}
	@echo "==> Build frontend"
	${NPM} --prefix ${WEB} run prepare
	${NPM} --prefix ${WEB} run build

${SERVER_BUNDLE}: ${SERVER_DEPS} ${SERVER_SRCS}
	@echo "==> Build backend"
	${NPM} --prefix ${SERVER} run prepare
	${NPM} --prefix ${SERVER} run build

clean:
	rm -rf ${SERVER_BUNDLE}
	rm -rf ${SERVER_DEPS}
	rm -rf ${WEB_DIST}
	rm -rf ${WEB_DEPS}

install: ${SERVER_BUNDLE} ${WEB_DIST}
	mkdir -p ${DATA} ${BINDIR}
	cp ${SERVER_BUNDLE} ${DATA}/turingarena.js
	cp -r ${WEB_DIST} ${DATA}/web
	echo "#!/usr/bin/env node\nrequire('${DATA}/turingarena.js');" > ${EXE}
	chmod +x ${EXE}

.PHONY: all build clean install