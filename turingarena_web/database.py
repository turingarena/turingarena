from collections import namedtuple
from contextlib import contextmanager
from enum import Enum
from typing import ContextManager, Optional, List

import bcrypt
import psycopg2.extensions
from flask import current_app

UserPrivilege = Enum("UserPrivilege", dict(STANDARD="STANDARD", ADMIN="ADMIN", TUTOR="TUTOR"))
User = namedtuple("User", ["id", "first_name", "last_name", "username", "email", "privilege"])
Submission = namedtuple("Submission", ["id", "problem_id", "user_id", "timestamp", "filename", "path"])
Problem = namedtuple("Problem", ["id", "name", "title", "location", "path"])
Goal = namedtuple("Goal", ["id", "problem_id", "name"])
EvaluationEventType = Enum("EvaluationEventType", dict(TEXT="TEXT", DATA="DATA"))
EvaluationEvent = namedtuple("EvaluationEvent", ["submission_id", "serial", "type", "data"])


class Database:
    @property
    @contextmanager
    def _connection(self) -> psycopg2.extensions.connection:
        connection = psycopg2.connect(
            dbname=current_app.config["DB_NAME"],
            user=current_app.config["DB_USER"],
            password=current_app.config["DB_PASS"]
        )
        yield connection
        connection.commit()
        connection.close()

    @property
    @contextmanager
    def cursor(self) -> ContextManager[psycopg2.extensions.cursor]:
        with self._connection as conn:
            with conn.cursor() as cursor:
                yield cursor


class UserDatabase(Database):
    def authenticate(self, username, password) -> bool:
        with self.cursor as cursor:
            cursor.execute("SELECT password FROM _user WHERE username = %s", (username,))
            if cursor.rowcount != 1:
                return False
            hashed_password = cursor.fetchone()
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password[0].encode("utf-8"))

    def get_by_username(self, username: str) -> Optional[User]:
        with self.cursor as cursor:
            cursor.execute("SELECT id, first_name, last_name, username, email, privilege FROM _user WHERE username = %s", (username,))
            result = cursor.fetchone()
        return User(*result) if result else None

    def get_by_id(self, id: int) -> Optional[User]:
        with self.cursor as cursor:
            cursor.execute("SELECT id, first_name, last_name, username, email, privilege FROM _user WHERE id = %s", (id,))
            result = cursor.fetchone()
        return User(*result) if result else None

    def insert(self, *, first_name, last_name, username, email, password) -> bool:
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

    def delete(self, user: User):
        with self.cursor as cursor:
            cursor.execute("DELETE FROM _user WHERE id = %s", (user.id,))


class ProblemDatabase(Database):
    def get_all(self) -> List[Problem]:
        with self.cursor as cursor:
            cursor.execute("SELECT * FROM problem")
            return [
                Problem(*result)
                for result in cursor
            ]

    def get_by_name(self, name) -> Optional[Problem]:
        with self.cursor as cursor:
            cursor.execute("SELECT * FROM problem WHERE name = %s", (name,))
            if cursor.rowcount == 1:
                return Problem(*cursor.fetchone())
            else:
                return None

    def insert(self, name, title, location, path, goals=None) -> bool:
        with self.cursor as cursor:
            try:
                cursor.execute("INSERT INTO problem(name, title, location, path) VALUES (%s, %s, %s, %s) RETURNING id",
                               (name, title, location, path))
                problem_id = cursor.fetchone()[0]
            except psycopg2.IntegrityError:
                return False
        if goals is not None:
            for goal in goals:
                cursor.execute("INSERT INTO goal(problem_id, name) VALUES (%s, %s)", (problem_id, goal))
        return True

    def delete(self, problem: Problem):
        with self.cursor as cursor:
            cursor.execute("DELETE FROM problem WHERE id = %s", (problem.id,))
            cursor.execute("DELETE FROM goal WHERE problem_id = %s", (problem.id,))


class SubmissionDatabase(Database):
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


class EvaluationEventDatabase(Database):
    def insert(self, *, submission_id, type, data):
        with self.cursor as cursor:
            cursor.execute("INSERT INTO evaluation_event(submission_id, type, data) VALUES (%s, %s, %s)",
                           (submission_id, type, data))

    def get_all(self, submission_id: int) -> List[EvaluationEvent]:
        with self.cursor as cursor:
            cursor.execute("SELECT * FROM evaluation_event WHERE submission_id = %s", (submission_id,))
            return [
                EvaluationEvent(*row)
                for row in cursor
            ]

    def get_event_after(self, submission_id: int, event_id: int) -> Optional[EvaluationEvent]:
        with self.cursor as cursor:
            cursor.execute(
                "SELECT * FROM evaluation_event WHERE submission_id = %s AND serial > %s ORDER BY serial LIMIT 1",
                (submission_id, event_id)
            )
            if cursor.rowcount == 0:
                return None
            if cursor.rowcount == 1:
                return EvaluationEvent(*cursor.fetchone())
            assert False
