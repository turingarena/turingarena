set -ex
( cd easy1/ && task-maker )
rm -f database.sqlite3
cargo run -- init-db
cargo run -- add-user test Test test
cargo run -- add-problem easy1 $PWD/easy1
cargo run -- serve --skip-auth 1
