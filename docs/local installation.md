# Local installation

This file explains how to performa a local installation of TuringArena. 
A local installation is an installation where you execute TuringArena directely from your Linux distribution instead of using 
a docker container. That is useful for developement purposes, or if you don't have/want to install docker on your machine. 

### Installing the required dependencies

First at all, you obviously need a Linux distribution. 

Then, you need to install the following dependencies:
- Python version 3.6 or higher, Python 3.5 is not supported 
- pip, the python package manager
- GCC, for compiling C/C++ programs 
- the package `libseccomp-dev`, if you are on Ubuntu/Debian
- jq, wich is a command for manipulating json files
- (optional) an installation of the Java JDK, for executing Java solution (optional)

You can install these dependencies on Ubuntu/Debian with:
```bash
sudo apt install python3.6 python3-pip build-essential libseccomp-dev jq openjdk-8-jdk
```

Then you can install the following python packages:
```bash
sudo pip3 install pip3 install bidict boto3 coloredlogs commonmark docopt pyyaml pytest-sugar pytest-xdist psutil seccomplite pytest tatsu networkx
```

### Installing TuringArena

First at all, you need to clone this repository, if you didn't already done it:
```bash
git clone https://github.com/turingarena/turingarena
cd turingarena/
```

Then, we need to install 4 components.

First, the cli interface:
```bash 
cd cli/
sudo python3 setup.py install 
cd ../
```

Then, the backend:
```bash
cd libraries/python/
sudo python3 setup.py install 
cd ../../
```

And then, the backend:
```bash
cd backend/
sudo python3 setup.py install 
cd ../
```

Now, a last thing that you need to do if you want the C++ evaluator to work is to copy the `turingarena.h` file in your include directory:
```bash
sudo cp libraries/cpp/turingarena.h /usr/local/include/
```

And you are done, now you can test your local installation with an example problem:
```bash
cd examples/sum_of_two_numbers/
turingarena -l evaluate solutions/correct.cpp
```
