ARG DEPLOY_BASE_IMAGE=turingarena/turingarena-deploy-base
FROM $DEPLOY_BASE_IMAGE

COPY . /src
