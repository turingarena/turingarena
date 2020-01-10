from __future__ import annotations

import yaml

from os import path
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

from turingarena.archive import Archive


@dataclass
class Problem:
    name: str
    path: str

    @staticmethod
    def from_data(name: str, directory: str) -> Problem:
        return Problem(
            name=name,
            path=path.join(directory, name)
        )

    @property
    def archive(self) -> Archive:
        return Archive.create(self.path)

    def to_graphql(self) -> dict:
        return dict(
            name=self.name,
            archiveContent=self.archive.to_graphql(),
        )


@dataclass
class User:
    id: str
    name: str
    token: str
    role: str

    @staticmethod
    def from_data(data: dict) -> User:
        return User(
            id=data["id"],
            name=data["name"],
            token=data["token"],
            role=getattr(data, "role", "user"),
        )

    @staticmethod
    def from_italy_yaml(data: dict) -> User:
        return User(
            id=data["username"],
            name=data["first_name"] + " " + data["last_name"],
            token=data["password"],
            role="user"
        )

    def to_turingarena_yaml(self):
        return self.__dict__

    def to_graphql(self) -> dict:
        return dict(
            id=self.id,
            displayName=self.name,
            token=self.token,
        )


@dataclass
class Contest:
    title: str
    start: Optional[datetime]
    end: Optional[datetime]
    users: List[User]
    problems: List[Problem]
    path: str

    @staticmethod
    def from_italy_yaml(directory: str) -> Contest:
        manifest = path.join(directory, "contest.yaml")

        if not path.exists(manifest):
            raise RuntimeError("Not a Italy YAML contest directory")

        with open(manifest) as f:
            data = yaml.load(f, Loader=yaml.SafeLoader)

        problems = list(map(lambda p: Problem.from_data(p, directory), data["tasks"]))
        users = list(map(lambda u: User.from_italy_yaml(u), data["users"]))

        return Contest(
            title=data["description"],
            start=datetime.fromtimestamp(data["start"]) if "start" in data else datetime.now(),
            end=datetime.fromtimestamp(data["stop"]) if "stop" in data else datetime(2050, 0, 0, 0, 0, 0),
            path=directory,
            problems=problems,
            users=users,
        )

    @staticmethod
    def from_directory(directory: str) -> Contest:
        manifest = path.join(directory, "turingarena.yaml")

        if not path.exists(manifest):
            raise RuntimeError("Not a TuringArena contest directory")

        with open(manifest) as f:
            data = yaml.load(f, Loader=yaml.SafeLoader)

        problems = list(map(lambda p: Problem.from_data(p, directory), data["problems"]))
        users = list(map(lambda u: User.from_data(u), data["users"]))

        # Write contest title in title.txt
        # TODO: change that
        with open(path.join(directory, "files", "title.txt"), "w") as f:
            f.write(data["title"])

        return Contest(
            title=data["title"],
            start=data["start"] if "start" in data else datetime.now(),
            end=data["end"] if "end" in data else datetime(2050, 0, 0, 0, 0, 0),
            path=directory,
            problems=problems,
            users=users,
        )

    def to_turingarena_yaml(self):
        return dict(
            title=self.title,
            start=self.start.isoformat(),
            end=self.end.isoformat(),
            problems=list(map(lambda p: p.name, self.problems)),
            users=list(map(lambda u: u.to_turingarena_yaml(), self.users))
        )

    @property
    def archive(self) -> Archive:
        return Archive.create(path.join(self.path, "files"))

    def to_graphql(self) -> dict:
        return dict(
            startTime=self.start.isoformat() + "Z",
            endTime=self.end.isoformat() + "Z",
            archiveContent=self.archive.to_graphql(),
        )
