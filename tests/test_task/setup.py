from setuptools import setup, find_packages

setup(
    name="test_challenge",
    packages=find_packages(),
    package_data={
        '': ['protocol.txt'],
    },
)
