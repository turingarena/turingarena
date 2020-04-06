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
