import bcrypt
import json
import os

from collections import namedtuple


class User(namedtuple("User", ["first_name", "last_name", "username", "password"])):
    @staticmethod
    def users(contest):
        with open(os.path.join(contest.directory, "users.jsonl")) as f:
            return [
                User.from_json_data(json.loads(line))
                for line in f
            ]

    @staticmethod
    def from_json_data(data):
        return User(
            username=data["username"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            password=data["password"],
        )

    @staticmethod
    def from_username(contest, username):
        for user in User.users(contest):
            if user.username == username:
                return user
        return None

    def check_password(self, password):
        if self.password.startswith("$"):
            return bcrypt.checkpw(password.encode("utf-8"), self.password.encode("utf-8"))
        else:
            print(password, "==", self.password)
            return password == self.password

    def as_json_data(self):
        return {
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "password": self.password,
        }

