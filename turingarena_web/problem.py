import logging
import os
import subprocess

from turingarena.evallib.metadata import load_metadata
from turingarena.file.generated import PackGeneratedDirectory
from turingarena_web.database import database
from turingarena_web.config import config


def clone_from_git(url, directory):
    os.mkdir(directory)
    logging.debug(f"git clone {url} -> {directory}")
    subprocess.call(["git", "clone", url, directory])


def generate_problem_files(problem_dir, name):
    files_dir = os.path.join(problem_dir, ".generated")
    os.mkdir(files_dir)

    pd = PackGeneratedDirectory(problem_dir, allowed_languages=config.get("ALLOWED_LANGUAGES", None))

    for path, generator in pd.targets:
        directory = os.path.join(files_dir, os.path.split(path)[0])
        filename = os.path.split(path)[1]
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, filename), "w") as file:
            generator(file)

    files_zip = os.path.join(problem_dir, f"{name}.zip")
    os.chdir(files_dir)
    subprocess.call(["zip", "-r", files_zip, "."])


def install_problem(location, name=None, title=None):
    if title is None:
        title = name
    if name is None:
        name = os.path.basename(location)

    problem_dir = config["PROBLEM_DIR_PATH"].format(name=name)

    if os.path.exists(problem_dir):
        subprocess.call(["rm", "-rf", problem_dir])

    clone_from_git(location, problem_dir)
    generate_problem_files(problem_dir, name)

    metadata = load_metadata(problem_dir)
    scoring_metadata = metadata.get("scoring", {})
    goals = scoring_metadata.get("goals", [])

    database.insert_problem(name=name, title=title, location=location, path=problem_dir, goals=goals)


def update_problem(name):
    problem = database.get_problem_by_name(name=name)

    # TODO: need to update goals?

    os.chdir(problem.path)
    subprocess.call(["git", "pull"])


def delete_problem(name):
    problem = database.get_problem_by_name(name)
    subprocess.call(["rm", "-rf", problem.path])
    database.delete_problem(problem.id)

