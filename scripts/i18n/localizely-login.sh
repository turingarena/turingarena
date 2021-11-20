xdg-open https://app.localizely.com/account
sleep 0.5
read -s -r -p 'Localizely API Token: ' TOKEN
echo
mkdir -p temp
echo $TOKEN > temp/localizely-api-token.txt
