set -xe

echo "VERSION='$CLI_VERSION'" > /src/cli/turingarena_cli/build_version.py

cd /src/cli
python3 setup.py egg_info bdist_wheel
twine upload dist/*
