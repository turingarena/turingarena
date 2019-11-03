#!/bin/bash 

set -ex
cargo build
for d in easy*/ ; do
    ( cd $d/testo/ && rm -f testo.pdf && latexmk -pdf testo.tex )
done
rm database.sqlite3
cargo run --package turingarena-contest-cli -- init-db
cargo run --package turingarena-contest-cli -- import-file contest.yaml
cargo run --features web-content -- serve --secret-key secret
