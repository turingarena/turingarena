import random

from turingarena_web.database import UserDatabase, ProblemDatabase


def test_user_database(app):
    user_db = UserDatabase()

    username = f"user_test_{random.randint(0, 1_000_000)}"
    password = f"user_pass_{random.randint(0, 1_000_000)}"

    user = dict(
        first_name=username,
        last_name=username,
        username=username,
        email=f"{username}@example.com",
        password=password,
    )

    assert user_db.insert(**user)
    assert not user_db.insert(**user)

    user = user_db.get_by_username(username)
    assert user.first_name == username

    assert user_db.authenticate(username, password)
    assert not user_db.authenticate(username, "WRONG")

    user_db.delete(user)
    assert user_db.get_by_username(username) is None


def test_problem_database(app):
    problem_db = ProblemDatabase()

    name = f"problem_{random.randint(0, 1_000_000)}"
    problem = dict(
        name=name,
        title=f"TuringArena problem {name}",
        location=f"example/{name}",
    )

    assert problem_db.insert(**problem)
    assert not problem_db.insert(**problem)

    problem = problem_db.get_by_name(name)
    assert problem is not None
    assert problem.name == name

    problem_db.delete(problem)
    assert problem_db.get_by_name(name) is None
