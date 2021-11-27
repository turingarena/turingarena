SQL="INSERT OR REPLACE INTO \
    package_location_data (package_id, location_name, path, created_at, updated_at) \
VALUES \
    ('contests/default', 'default', 'examples/example-contest', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) \
;"

echo $SQL

sqlite3 server/db.sqlite3 "$SQL"
git push $PWD/server/db.git develop:main
