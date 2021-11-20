read TOKEN < temp/localizely-api-token.txt
read PROJECT_ID < scripts/i18n/localizely-project-id.txt

( cd web/ && npx formatjs extract --format simple 'src/**/*.tsx' ) > temp/translations-main.json

curl \
    -X POST \
    "https://api.localizely.com/v1/projects/$PROJECT_ID/files/upload?lang_code=en&overwrite=true&tag_added=added&tag_removed=removed&tag_updated=updated" \
    -H "accept: */*" \
    -H "X-Api-Token: $TOKEN" \
    -H "Content-Type: multipart/form-data" \
    -F "file=@temp/translations-main.json;type=application/json"
