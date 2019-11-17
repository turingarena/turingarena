#!/bin/bash 

set -ex

rm -f database.sqlite3

RUN="cargo run --package turingarena --all-features --offline"

$RUN -- --problems-dir $PWD admin init-db

for d in easy*/ ; do
    ( cd $d/testo/ && rm -f testo.pdf && latexmk -pdf testo.tex )
    ( cd $d/ && rm -rf .task-maker-files/ )
done

$RUN -- --problems-dir $PWD admin import-file contest.yaml
$RUN -- --problems-dir $PWD serve --secret-key secret
