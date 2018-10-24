ARG TURINGARENA_IMAGE=turingarena/turingarena
ARG DEPLOY_BASE_IMAGE=turingarena/turingarena-deploy-base

FROM $TURINGARENA_IMAGE as src
FROM $DEPLOY_BASE_IMAGE

COPY --from=src /usr/local/turingarena/ /src/
COPY deploy.sh deploy.sh

CMD sh deploy.sh
