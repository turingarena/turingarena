#!/bin/bash 

set -ex
( cd easy1/testo/ && rm -f testo.pdf && latexmk -pdf testo.tex )
rm -f database.sqlite3
cargo run -- --problems-dir $PWD init-db "Test contest"
for i in {1..10}; do 
    cargo run -- --problems-dir $PWD add-user "user$i" "User #$i" "user$i"
done
cargo run -- --problems-dir $PWD add-user test Test test
cargo run -- --problems-dir $PWD add-problem easy1
cargo run --features web-content -- --problems-dir $PWD serve --skip-auth 1 --secret-key secret
