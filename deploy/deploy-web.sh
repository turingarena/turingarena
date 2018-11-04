set -xe

cd /src/web/

lerna bootstrap
lerna run build
surge --project packages/ui/build/ --domain $SURGE_DOMAIN
