# TuringArena

[![Join the chat at https://gitter.im/turingarena/turingarena](https://badges.gitter.im/turingarena/turingarena.svg)](https://gitter.im/turingarena/turingarena?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

*Create algorithmic challenges!*

[TuringArena](http://turingarena.org "TuringArena") is a toolkit and platform which allows to:

* define challenges which require an algorithmic solution;
* get/provide automatic evaluation of submitted solutions for an immidiate feedback to the problem recipient (student, class, employee/user/costumer to be trained/evaluated upon some competences), or for problem/system testing for the problem maker or proposer (teacher, trainer, advisor), or for student/team evaluation purposes;
* allow and organize the immediate use, the shared development, the publication and the promoting of the problem with possibly an eye to the respecting of the paternity and intellectual property of the problems that we fully recognize as forms of valuable content (we ourselves started this up as problem developers as part of our service for the italian olympiads in informatics and within our classes).

Some of the innovative features are:

* a language independent workflow, the problem designer is required a basic knowledge in just one programming language of its choice, and can always decide to which languages the evaluation service of solutions is open;
* virtually no restriction on the generality of challenges that can be represented;
* support for defining and implementing with minimum effort meaty problems from various fields (mainly in computer science and mathematics, but let's offer more concrete hints: algorithms, reductions between problems, computational complexity, games in a broad sense, mathematical programming, criptography, zero-knowledge proofs, programming tasks in specific languages or environments, workflows, ... and even support for problem solving without programming);  
* high levels of interactivity allowed and open ends for gamifications;
* an effective problem sharing approach which allows teachers and the like to organize in networks collaborating to the joint development of problem based didactive projects for the active learner and open source publishing the problems without neither spoiling them nor giving up their paternity, possibly even copyrighting them.


## Getting started

Here is how to use TuringArena on your local machine to develop and test challenges.

### Prerequisites

TuringArena is currently supported *only on Linux*, because we use
Linux-specific kernel interfaces to sandbox submissions and measure resource utilization. 

To use TuringArena on a local machine, the following tools are needed:
- `python3.6` or newer
- `pip`
- `gcc and g++` for compiling C/C++ submissions
- `libseccomp-dev` used for the submission sandbox
- `jq` used to format json output
- on Ubuntu/Debian, `python3-dev` for addictional header files 

You may also want the following optional dependencies:
- `openjdk-*-jdk` to run Java submissions
- `rustc` to run Rust submissions 
- `ruby` to run Ruby submissions
- `pipenv` to install in a virtual environment 

To install all of these dependencies on Ubuntu 18.04:
```bash
sudo apt install python3.6 python3-pip build-essential jq libseccomp-dev 
```

### Install / Upgrade
To install the TuringArena core, run the `setup.py` inside `src`. 
```bash
cd src/
python3 setup.py develop
```

To install the TuringArena web interface, run the `setup.py` inside `taserver`. 
```bash
cd taserver/
python3 setup.py develop
```
You may want to execute these commands inside a virtual environment. 

#### Install using Pipenv (recommended)
You can install TuringArena with `pipenv`, this will install both the 
core and the web interface in a virtual environment automatically. 

Simply run `pipenv install` in the root directory of this repository, 
and then use `pipenv shell` to open a shell inside the created virtual environment. 

### Usage

To evaluate a solution, `cd` in the directory of the problem and run:
```bash
turingarena-dev evaluate path/to/solution.cpp
```

### First tests (running the example problems)

1. Clone this repository.
```bash
git clone https://github.com/turingarena/turingarena.git
```
2. `cd` into any of the example problem directories. Example:
```bash
cd examples/sum_of_two_numbers/
```
3. Evaluate a solution, say, `correct.cpp`:
```bash
turingarena-dev evaluate solutions/correct.cpp
```
