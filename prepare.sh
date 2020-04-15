#!/bin/bash

set -ex

( cd server/ ; npm ci )
( cd web/ ; npm ci )

if [ -f server/db.sqlite3 ] ; then
    mv server/db.sqlite3 server/db.sqlite3.bak
fi

( cd server/ ; npm run cli -- import ../examples/example-contest/ )
