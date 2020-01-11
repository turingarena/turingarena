#!/bin/bash

set +xe

cd examples/example-contest

rm -f database.sqlite3

RUN="cargo run -vv --package turingarena --all-features --offline"

for d in easy*/ ; do
    ( cd $d/testo/ && latexmk -pdf testo.tex )
done

$RUN -- admin init-db
$RUN -- admin import-file contest.yaml
$RUN -- admin add-user --admin --id admin --display-name "Super Admin" --token admin
$RUN -- admin update-contest --path $PWD
for p in easy1 easy2 easy3 ; do
    $RUN -- admin add-problem --name $p --path $p/
done

$RUN -- serve --enable-dmz --secret-key secret
