# TuringArena

*Create algorithmic challenges!*

TuringArena is a toolkit to define challenges which require an algorithmic solution,
and to automatically test the code of solutions.

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

## Update the Docker image

Run the following regularly, to update the server.
```bash
sudo docker pull turingarena/turingarena
```