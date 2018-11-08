# configuration file for TuringArena Web

# debug mode
DEBUG = True

# secret key - set a random value in production
SECRET_KEY = "ciao"

# database credentials
DB_NAME = "turingarena"
DB_USER = "turingarena"
DB_PASS = "turingarena"
DB_HOST = "localhost"

# where to put problem files
PROBLEM_DIR_PATH = "/home/ale/tweb/problem/{name}"

# where to save submission for problems
SUBMITTED_FILE_PATH = "/home/ale/tweb/submission/{username}/{problem_name}/{timestamp}_{filename}"
