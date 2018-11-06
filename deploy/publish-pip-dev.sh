set -xe

cd /src/src

echo "$CLI_VERSION" > version.txt
echo "VERSION='$CLI_VERSION'" > turingarena/build_version.py

python3 setup.py egg_info bdist_wheel
twine upload dist/*
