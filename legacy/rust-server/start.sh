#!/bin/sh

CLI="$PWD/cli.sh"
CONTEST="$PWD/examples/example-contest"

export DATABASE="$PWD/database.sqlite3"
export SECRET="secret"

rm -f $DATABASE
cargo build --package turingarena-web-server --all-features

(

for d in $CONTEST/easy*/ ; do
    ( cd $d/testo/ && latexmk -pdf testo.tex )
done

# Import current contest
$CLI init-db
$CLI import --path "$CONTEST" 

)&

cargo run --package turingarena-web-server --all-features -- --enable-dmz 
