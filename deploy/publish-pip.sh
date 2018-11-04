set -xe

cd /src/src

echo "VERSION='$CLI_VERSION'" > turingarena_common/build_version.py
python3 setup.py egg_info bdist_wheel
twine upload dist/*
