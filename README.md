# Turingarena

![CI testing](https://github.com/turingarena/turingarena/workflows/CI%20testing/badge.svg)

A collection of libraries and tools to create programming challenges and competitions.

## Getting started

1. Make sure to have (a recent version of) Node and NPM installed and in `PATH`.
2. Make sure to have installed [tmux](https://github.com/tmux/tmux/wiki/Installing)
3. To install dependencies, run:

```bash
    ( cd server/ ; npm ci )
    ( cd web/ ; npm ci )
```

**Possible issue**

_On Ubuntu 18.04 (and maybe other older version) the NPM could not be updated to the latest version available with a default installation.
This could make the previous code to not work because it is not recognizing the comand `npm ci`.
To fix this problem you need to upgrade to a recent version of NPM running:_

```bash
    curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -
    sudo apt-get install -y nodejs
```

4. Import the example contest with:

```bash
    ( cd server/ ; npm run cli -- import ../examples/example-contest/ )
```

5. TODO: running the server in production

## Using Docker

You can run this application with Docker, to have a system ready to use, that you can also use on macOS or Windows.

1. Build the Docker container (at this point we don't provide prebuilt ones)

```bash
docker build . -t turingarena:turingarena
```

It will probably take a few minutes, so go to drink a cofee while the system build everything.

2. Start the server like this

```bash
docker run --privileged -it -p 3000:3000 -v $PWD/server:/data turingarena:turingarena serve
```

Of course change the port or the working directory (/data) as you wish. It's important to use the `--privileged` option,
otherwise the sandbox will not work. You may need root privileges on your system to use that.
