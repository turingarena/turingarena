set -xe

echo "VERSION='$CLI_VERSION'" > /src/src/turingarena/build_version.py

cd /src/src
python3 setup.py egg_info bdist_wheel
twine upload dist/*
