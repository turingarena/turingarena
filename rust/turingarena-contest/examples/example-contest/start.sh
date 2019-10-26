#!/bin/bash 

set -ex
( cd easy1/testo/ && rm -f testo.pdf && latexmk -pdf testo.tex )
rm -f database.sqlite3
cargo run -- init-db "Test contest"
for i in {1..10}; do 
    cargo run -- add-user "utente$i" "Utente $i" "utente$i"
done
cargo run -- add-user test Test test
cargo run -- add-problem easy1 $PWD/easy1
cargo run -- serve --skip-auth 1
