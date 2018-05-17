# TuringArena

*Create algorithmic challenges!*

[TuringArena](http://turingarena.org "TuringArena") is a toolkit and platform which allows to:

* define challenges which require an algorithmic solution;
* get/provide automatic evaluation of submitted solutions for an immidiate feedback to the problem recipient (student, class, employee/user/costumer to be trained/evaluated upon some competences), or for problem/system testing for the problem maker or proposer (teacher, trainer, advisor), or for student/team evaluation purposes;
* allow and organize the immidiate use, the shared development, the publication and the promoting of the problem with possibly an eye to the respecting of the paternity and intellectual property of the problems that we fully recognize as forms of valuable content (we ourselves started this up as problem developers as part of our service for the italian olympiads in informatics and within our classes). 

Some of the innovative features are:

* a language independent workflow, the problem designer is required a basic knowledge in just one programming language of its choice, and can always decide to which languages the evaluation service of solutions is open;
* virtually no restriction on the generality of challanges that can be represented;
* support for defining and implementing with minimum effort meaty problems from various fields (mainly in computer science and mathematics, but let's offer more concrete hints: algorithms, reductions between problems, computational complexity, games in a broad sense, mathematical programming, criptography, zero-knowledge proofs, programming tasks in specific languages or environments, workflows, ... and even support for problem solving without programming);  
* high levels of interactivity allowed and open ends for gamifications;
* an effective problem sharing approach which allows teachers and the like to organize in networks collaborating to the joint development of problem based didactive projects for the active learner and open source publishing the problems without neither spoiling them nor giving up their paternity, possibly even copyrighting them.


## Getting started

Here is how to use TuringArena on your local machine to develop and test challenges.

### Prerequisites

TuringArena is currently supported *only on Linux*.
To use TuringArena on a local machine, the following tools are needed:

- **Python** and **pip**
([how to install](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)),
used to install and run the CLI client
- **Docker CE** 
([how to install](https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-docker-ce)),
used to run the CLI server
- **Git** ([how to install](https://git-scm.com/download/linux)),
used internally to send data to and from the CLI server.

### Installation

1. Clone this repository.
```bash
git clone https://github.com/turingarena/turingarena.git
```
2. `cd` into the cloned repository directory
```bash
cd turingarena/
```
3. Install the CLI client
(you may prefer to use a *virtualenv* or the `--user` option to install for the current user only, see
[this tutorial](https://packaging.python.org/tutorials/installing-packages/#installing-from-a-local-src-tree))
```bash
sudo pip install -e .
```

### Usage

To start the server, run:
```bash
sudo turingarenad
```

You can terminate the server by pressing `Ctrl-C`.

At the moment, to work on a challenge, the code must be placed in a (local) Git repository.

To evaluate a solution, `cd` in the directory of the problem and run:
```bash
turingarena evaluate path/to/solution.cpp
```

## First tests (running the example problems)

1. `cd` into any of the example problem directories. Example:
```bash
cd examples/sum_of_two_numbers/
```
2. Evaluate a solution, say, `correct.cpp`:
```bash
turingarena evaluate solutions/correct.cpp
```
3. Test all the provided solutions:
```bash
turingarena test
```
