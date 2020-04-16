# Turingarena
![CI testing](https://github.com/turingarena/turingarena/workflows/CI%20testing/badge.svg)

A collection of libraries and tools to create programming challenges and competitions.

## Getting started

1. Make sure to have (a recent version of) Node and NPM installed and in `PATH`.
2. To install dependencies, run:

```bash
    ( cd server/ ; npm ci )
    ( cd web/ ; npm ci )
```

3. Import the example contest with:

```bash
    ( cd server/ ; npm run cli -- import ../examples/example-contest/ )
```

4. The `start.sh` scripts creates a `tmux` sessions with all the commands needed to develop running in parallel. Warning: can impact the use of CPU and RAM. Either use the script or inspect the scripts in `web/package.json` and `server/package.json` and run them individually as needed.
To use the script, run:

```bash
    ./start.sh
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