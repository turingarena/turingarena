# TuringArena server

TuringArena now comes with a server that exposes a web interface. 

## Installation

First at all, you need to setup a Postgres database, with the following commands:
```bash
sudo su postgres
createuser --pwprompt turingarena
createdb --owner=turingarena turingarena
psql --dbname=turingarena --command 'ALTER SCHEMA public OWNER TO turingarena' 
```

Next, you need to take the example configuration file (in `etc/turingarena.conf`) and put it in one of the following paths:
- `/etc/turingarena.conf`
- `/urs/local/etc/turingarena.conf`

Or you can specify a different path setting the environment variable `TA_CONFIG_FILE `.

Next edit this file and change the various setting, for example you may want to specify your DB credentials and change 
the paths of the submissions and contest directories. Remember to also change the `SECRET_KEY` with a random value that 
only you knows. 

Then to start a development server, use `tactl run server`. 

## Usage

### Users
A user can be add in different ways: it can be added from the command line, with `tactl user add <username>` or a user can register
himself from the web interface, if registration is allowed. You can remove users only from the command line. A user 
can have different privileges (`STANDARD`, `TUTOR`, `ADMIN`), that you can set from the command line (for now this feature is not unused).

### Contests
To create a contest, you simply create a directory in the path you specified in the configuration file. The name of that 
directory will be the name of the contest. A contest can contain a `Turingfile` to specify additional options, here 
is an example of a contest Turingfile:
```toml
[contest]
# the title of the contest that will apper in the interface
title = "Title" 

# if public all users can view the contest, defaults to false
public = true 

# restrict the languages that can be used in this contest
languages = ["Python", "C++", "Rust"] 
```  

If a contest is not defined as public you must manually add a user to the contest, with `tact contest add_user <username> <contest>`.

### Problems

A contest contains zero or more problems. A problem must be placed in a directory inside the contest directory, and the 
name of the directory is the name of the problem. Like the contest, a problem can have an optional `Turingfile` that 
controls some metadata. Example of problem `Turingfile`:
```toml
[problem]
# like before, title of the problem
title = "Title"

[scoring]
# in this section, information legated to the scoring, like the goals of the problem
goals = ["goal1", "goal2"]
```

To be usable from the web interface, you need to sync the files of the problem, and also generate the zip: you can do 
that with the command `turingarena-dev file sync --zip -f`. Remember to execute this command again each time you do 
some changes to the problem!

### Submissions

The submissions are saved to the directory specified in the `turingarena.conf` file. For each submission, you can find 
in the directory:
- a file `events.jsonl`, the events produces by the evaluation as json lines
- the files submitted by the user

## API

The server exposes a REST API, you can find that at `/api/<method>`, where method is one of the following:
- `events(id, after)`, to get evaluation event of submission `id` starting from the event whose position is after `after`
- `submission(id)`, to get the submission details of submission with id `id`
- `user(username)`, to get details about the specified user
- `contest(contest)`, to get information about the specified contest
- `problem(contest, problem)`, to get problem information
- `auth(username, password)`, to authenticate to the system 

All the API besides `auth` require you to be authenticated. 