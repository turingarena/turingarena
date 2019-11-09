#!/bin/bash 

set -ex
cargo build
for d in easy*/ ; do
    ( cd $d/testo/ && rm -f testo.pdf && latexmk -pdf testo.tex )
    ( cd $d/ && rm -rf .task-maker-files/ )
done
rm -f database.sqlite3
cargo run --package turingarena-contest -- --problems-dir $PWD admin init-db
cargo run --package turingarena-contest -- --problems-dir $PWD admin import-file contest.yaml
cargo run --features web-content -- --problems-dir $PWD serve --secret-key secret
