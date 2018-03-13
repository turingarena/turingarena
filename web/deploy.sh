pushd build/

set -ex

git init
git checkout --detach
git branch -d master || true
git checkout --orphan master
git reset
git add .
git commit -m "Deploy"
git push -f git@github.com:turingarena/demo master:master

popd
