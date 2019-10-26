set -ex
( cd easy1/ && task-maker )
( cd easy1/testo/ && rm -f testo.pdf && latexmk -pdf testo.tex )
rm -f database.sqlite3
cargo run -- init-db "Test contest"
cargo run -- add-user test Test test
cargo run -- add-problem easy1 $PWD/easy1
cargo run -- serve --skip-auth 1
