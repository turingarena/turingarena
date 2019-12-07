#!/bin/bash 

set -ex

rm -f database.sqlite3

RUN="cargo run -vv --package turingarena --all-features --offline"

$RUN -- admin init-db

for d in easy*/ ; do
    ( cd $d/testo/ && rm -f testo.pdf && latexmk -pdf testo.tex )
    ( cd $d/ && rm -rf .task-maker-files/ )
done

$RUN -- admin import-file contest.yaml

$RUN -- admin update-contest --path $PWD

for p in easy1 easy2 easy3 ; do
    $RUN -- admin add-problem --name $p --path $p/
done

$RUN -- serve --skip-auth 1 --secret-key secret
