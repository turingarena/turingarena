set -xe

cd /src/cli

echo "$CLI_VERSION" > version.txt
echo "VERSION='$CLI_VERSION'" > turingarena_cli/build_version.py

python3 setup.py egg_info bdist_wheel
twine upload dist/*
