#!/bin/bash 

set -ex
( cd easy1/testo/ && rm -f testo.pdf && latexmk -pdf testo.tex )
cargo run import-contest --force contest.yaml
cargo run --features web-content -- --problems-dir $PWD serve --skip-auth 1 --secret-key secret
