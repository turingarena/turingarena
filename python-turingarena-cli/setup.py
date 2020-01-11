from setuptools import setup

setup(
    name="turingarena",
    version="1.0",
    description='TuringArena CLI interface',
    license="MPL-2.0",
    author="Alessandro Righi",
    author_email="alerighi4@gmail.com",
    url="http://github.com/turingarena/turingarena/",
    packages=['turingarena'],
    install_requires=["requests", "pyyaml"],
    entry_points={
        'console_scripts': [
            'turingarena = turingarena.turingarena:main',
        ],
    },
)
