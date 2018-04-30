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

1. Clone this repository and `cd` into it.
```bash
git clone https://github.com/turingarena/turingarena.git
cd turingarena/
```
2. Install the CLI client
(you may prefer to use a *virtualenv* or the `--user` option to install for the current user only, see
[this tutorial](https://packaging.python.org/tutorials/installing-packages/#installing-from-a-local-src-tree))
```bash
sudo pip install -e .
```

### Usage

To start the server, run (from the repository directory):
```bash
sudo sh start-server.sh
```

You can terminate the server by pressing `Ctrl-C`.

At the moment, to work on a challenge, the code must be placed in a (local) Git repository.

To evaluate a solution, `cd` in the directory of the problem and run:
```bash
turingarena evaluate <solution-file>
```
