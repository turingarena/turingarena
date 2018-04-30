from setuptools import setup

setup(
    name='turingarena',
    version='0.0',
    url='https://github.com/turingarena/turingarena',
    license='MPL 2.0',
    author='Massimo Cairo',
    author_email='cairomassimo@gmail.com',
    description='',
    packages=[],
    py_modules=['turingarena_cli'],
    entry_points={
        'console_scripts': [
            "turingarena=turingarena_cli:turingarena_cli",
        ],
    }
)
