# turingarena_web
Local web interface for the TuringArena project

### How to install

1) Install the required software:
    - python3.6
    - postgreSQL
    - turingarena (https://github.com/turingarena/turingarena)
    - a web server 
2) run `setup.py`
3) create a new postgreSQL database for turingarena
4) initialize the database running `tactl init`
5) copy the configuration file `etc/turingarena.conf` in `/etc` or `/usr/local/etc`
6) edit the configuration file, specifying the credentials of the database and paths for the files
7) configure a WebServer (like Apache or Ngnix) with WSGI to point to the application