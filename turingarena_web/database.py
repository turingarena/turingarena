from collections import namedtuple
from contextlib import contextmanager
from enum import Enum
from functools import lru_cache
from typing import ContextManager, Optional, List

import bcrypt
import psycopg2.extensions

from turingarena_web.config import config

UserPrivilege = Enum("UserPrivilege", dict(STANDARD="STANDARD", ADMIN="ADMIN", TUTOR="TUTOR"))
User = namedtuple("User", ["id", "first_name", "last_name", "username", "email", "privilege"])
Submission = namedtuple("Submission", ["id", "problem_id", "user_id", "timestamp", "filename", "path"])
Problem = namedtuple("Problem", ["id", "name", "title", "location", "path"])
Goal = namedtuple("Goal", ["id", "problem_id", "name"])
EvaluationEventType = Enum("EvaluationEventType", dict(TEXT="TEXT", DATA="DATA", END="END"))
EvaluationEvent = namedtuple("EvaluationEvent", ["submission_id", "serial", "type", "data"])


class Database:
    @property
    @lru_cache(None)
    def _connection(self) -> psycopg2.extensions.connection:
        connection = psycopg2.connect(
            dbname=config["database"]["name"],
            user=config["database"]["user"],
            password=config["database"]["pass"],
            host=config["database"]["host"],
        )
        return connection

    @property
    @contextmanager
    def cursor(self) -> ContextManager[psycopg2.extensions.cursor]:
        with self._connection:
            with self._connection.cursor() as cursor:
                yield cursor

    def query_all(self, *args):
        with self.cursor as cursor:
            cursor.execute(*args)
            for result in cursor:
                yield result

    def query_one(self, *args):
        with self.cursor as cursor:
            cursor.execute(*args)
            assert cursor.rowcount == 1
            return cursor.fetchone()

    def query(self, *args):
        with self.cursor as cursor:
            cursor.execute(*args)

    def user_authenticate(self, username, password) -> bool:
        with self.cursor as cursor:
            cursor.execute("SELECT password FROM _user WHERE username = %s", (username,))
            if cursor.rowcount != 1:
                return False
            hashed_password = cursor.fetchone()
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password[0].encode("utf-8"))

    def get_user_by_username(self, username: str) -> Optional[User]:
        with self.cursor as cursor:
            cursor.execute(
                "SELECT id, first_name, last_name, username, email, privilege FROM _user WHERE username = %s",
                (username,)
            )
            result = cursor.fetchone()
        return User(*result) if result else None

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        with self.cursor as cursor:
            cursor.execute(
                "SELECT id, first_name, last_name, username, email, privilege FROM _user WHERE id = %s",
                (user_id,)
            )
            result = cursor.fetchone()
        return User(*result) if result else None

    def get_users(self):
        with self.cursor as cursor:
            cursor.execute("SELECT id, first_name, last_name, username, email, privilege FROM _user")
            return [
                User(*r)
                for r in cursor
            ]

    def insert_user(self, *, first_name, last_name, username, email, password) -> bool:
        with self.cursor as cursor:
            hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("ascii")
            try:
                cursor.execute(
                    "INSERT INTO _user(first_name, last_name, username, email, password) VALUES (%s, %s, %s, %s, %s)",
                    (first_name, last_name, username, email, hashed_password)
                )
                return True
            except psycopg2.IntegrityError:
                return False

    def get_all_problems(self) -> List[Problem]:
        with self.cursor as cursor:
            cursor.execute("SELECT * FROM problem")
            return [
                Problem(*result)
                for result in cursor
            ]

    def get_problem_by_name(self, name) -> Optional[Problem]:
        with self.cursor as cursor:
            cursor.execute("SELECT * FROM problem WHERE name = %s", (name,))
            if cursor.rowcount == 1:
                return Problem(*cursor.fetchone())
            else:
                return None

    def insert_problem(self, name, title, location, path, goals=None) -> bool:
        with self.cursor as cursor:
            try:
                cursor.execute("DELETE FROM problem WHERE name = %s", (name,))
                cursor.execute("INSERT INTO problem(name, title, location, path) VALUES (%s, %s, %s, %s) RETURNING id",
                               (name, title, location, path))
                problem_id = cursor.fetchone()[0]
            except psycopg2.IntegrityError:
                return False
            if goals is not None:
                for goal in goals:
                    cursor.execute("INSERT INTO goal(problem_id, name) VALUES (%s, %s)", (problem_id, goal))
            return True

    def delete_problem(self, problem_id: int):
        with self.cursor as cursor:
            cursor.execute("DELETE FROM problem WHERE id = %s", (problem_id,))
            cursor.execute("DELETE FROM goal WHERE problem_id = %s", (problem_id,))

    def get_submissions_by_user(self, user: User) -> List[Submission]:
        with self.cursor as cursor:
            cursor.execute("SELECT * FROM submission WHERE user_id = %s", (user.id,))
            return [
                Submission(*row)
                for row in cursor
            ]

    def insert_submission(self, user_id: int, problem_id: int, filename: str, path: str) -> Optional[int]:
        with self.cursor as cursor:
            cursor.execute("""
                INSERT INTO submission(problem_id, user_id, filename, path) VALUES (%s, %s, %s, %s) RETURNING id
            """, (problem_id, user_id, filename, path))
            if cursor.rowcount == 1:
                return cursor.fetchone()[0]
            return None

    def get_submission_by_id(self, submission_id):
        with self.cursor as cursor:
            cursor.execute(
                "SELECT * FROM submission WHERE id = %s", (submission_id,)
            )
            if cursor.rowcount == 1:
                return Submission(*cursor.fetchone())
            return None

    def get_submissions_by_user_and_problem(self, *, user_id, problem_id):
        with self.cursor as cursor:
            cursor.execute("SELECT * FROM submission WHERE user_id = %s and problem_id = %s ORDER BY timestamp DESC", (user_id, problem_id))
            submissions = [Submission(*sub) for sub in cursor]
            cursor.execute("SELECT COUNT(*) FROM goal WHERE problem_id = %s", (problem_id,))
            n_goals = cursor.fetchone()[0]
            result = []
            for submission in submissions:
                cursor.execute("SELECT COUNT(*) FROM acquired_goal WHERE submission_id = %s", (submission.id,))
                solved_goals = cursor.fetchone()[0]
                result.append(dict(id=submission.id, timestamp=submission.timestamp, filename=submission.filename, goals=solved_goals, n_goals=n_goals))
            return result

    def insert_evaluation_event(self, *, submission_id, e_type, data):
        with self.cursor as cursor:
            cursor.execute("INSERT INTO evaluation_event(submission_id, type, data) VALUES (%s, %s, %s)",
                           (submission_id, e_type, data))

    def insert_goal(self, *, submission: Submission, name: str):
        with self.cursor as cursor:
            cursor.execute("""INSERT INTO acquired_goal(goal_id, submission_id) VALUES (
                (SELECT id FROM goal WHERE problem_id = %s AND name = %s), %s)
                """, (submission.problem_id, name, submission.id))

    def get_goals(self, submission_id):
        with self.cursor as cursor:
            cursor.execute("""
                SELECT g.name 
                FROM goal g JOIN problem p JOIN submission s ON p.id = s.problem_id ON g.problem_id = p.id
                WHERE s.id = %s
            """, (submission_id,))

            goals = {
                name[0]: False
                for name in cursor
            }

            cursor.execute(
                "SELECT g.name FROM acquired_goal ag JOIN goal g ON ag.goal_id = g.id WHERE ag.submission_id = %s",
                (submission_id,)
            )

            for name in cursor:
                goals[name[0]] = True

            return goals

    def get_all_evaluation_events(self, submission_id: int) -> List[EvaluationEvent]:
        with self.cursor as cursor:
            cursor.execute("SELECT * FROM evaluation_event WHERE submission_id = %s ORDER BY serial", (submission_id,))
            return [
                EvaluationEvent(*row)
                for row in cursor
            ]


database = Database()
