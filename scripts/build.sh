if [ $(python3 -c "import sys; print(hasattr(sys, 'real_prefix'))") = "False" ]; then
    echo "We recommend using a python virtualenv to use this software from source."
    echo
    echo "To install the needed software for virtual environments:"
    echo "  $ sudo apt-get install python3-virtualenv virtualenvwrapper"
    echo "  $ echo 'source /usr/local/bin/virtualenvwrapper_lazy.sh' >> ~/.bashrc"
    echo "  $ source ~/.bashrc"
    echo
    echo "To create a virtualenv:"
    echo "  $ mkvirtualenv -p /usr/bin/python3 taskwiz"
    echo
    echo "Then, to use your shiny virtual environment:"
    echo "  $ workon taskwiz"
    echo
    echo "If you want to exit the virtual environment:"
    echo "  $ deactivate"
    echo
    echo "After doing all of that, re-run this script!"
    exit 1
fi

pip install --requirement dev-requirements.txt
grako --name Grammar task-wizard/compiler/grammar.ebnf --output task-wizard/compiler/grammar.py

echo
echo "OK! Now (if you didn't already) you can install this software with:"
echo "  $ python setup.py develop"
