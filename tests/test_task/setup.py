from setuptools import setup, find_packages

setup(
    name="test_challenge",
    packages=["test_challenge"],
    package_data={
        'test_challenge': ['protocol.txt'],
    },
)
