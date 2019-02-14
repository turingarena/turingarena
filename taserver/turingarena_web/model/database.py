import logging
import pkgutil
from contextlib import contextmanager
from functools import lru_cache

import psycopg2.extensions

from turingarena_web.config import config


class Database:
    @property
    @lru_cache(None)
    def _connection(self) -> psycopg2.extensions.connection:
        connection = psycopg2.connect(
            dbname=config.database["name"],
            user=config.database["user"],
            password=config.database["pass"],
            host=config.database["host"],
        )
        return connection

    @property
    @contextmanager
    def cursor(self):
        with self._connection:
            with self._connection.cursor() as cursor:
                yield cursor

    def init(self):
        logging.debug(f"Loading initialization SQL...")
        # avoid pkg_resources overkill (non-stdlib and slower)
        initsql = pkgutil.get_data(__package__, "init.sql")
        logging.info(f"Initializing the database...")

        with self.cursor as cursor:
            cursor.execute(initsql)

        logging.info(f"Database initialized successfully.")

    def query_all(self, query, *args, convert=None):
        with self.cursor as cursor:
            cursor.execute(query, tuple(args))
            if convert is None:
                for x in cursor:
                    yield x
            for e in map(lambda x: convert(*x), cursor):
                yield e

    def query_one(self, query, *args, convert=None):
        with self.cursor as cursor:
            cursor.execute(query, tuple(args))
            if cursor.rowcount == 1:
                if convert is None:
                    return cursor.fetchone()
                return convert(*cursor.fetchone())
            return None

    def query_exists(self, query, *args):
        with self.cursor as cursor:
            cursor.execute(query, tuple(args))
            return cursor.rowcount >= 1

    def query(self, query, *args):
        with self.cursor as cursor:
            cursor.execute(query, tuple(args))


database = Database()
