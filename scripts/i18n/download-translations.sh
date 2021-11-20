read TOKEN < temp/localizely-api-token.txt
read PROJECT_ID < scripts/i18n/localizely-project-id.txt

curl \
    -X GET \
    "https://api.localizely.com/v1/projects/$PROJECT_ID/files/download?export_empty_as=main&type=json" \
    -H "accept: */*" \
    -H "X-Api-Token: $TOKEN" \
    > temp/translations.zip
mkdir -p temp/lang/
unzip -o temp/translations.zip -d temp/lang/

( cd web/ && npx formatjs compile-folder --ast --format simple ../temp/lang/ src/lang/ )
