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
    def from_data(data: dict):
        return User(
            id=data["id"],
            name=data["name"],
            token=data["token"],
            role=getattr(data, "role", "user"),
        )

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
    def from_directory(directory: str) -> Contest:
        manifest = path.join(directory, "turingarena.yaml")

        if not path.exists(manifest):
            raise RuntimeError("Invalid contest directory: turingarena.yaml missing")

        directory = path.abspath(directory)

        with open(manifest) as f:
            data = yaml.load(f, Loader=yaml.SafeLoader)

        problems = list(map(lambda p: Problem.from_data(p, directory), data["problems"]))
        users = list(map(lambda u: User.from_data(u), data["users"]))

        # Write contest title in title.txt
        # TODO: change that
        with open(path.join(directory, "files", "title.txt"), "w") as f:
            print(data["title"], file=f)

        return Contest(
            title=data["title"],
            start=data["start"] if "start" in data else datetime.now(),
            end=data["end"] if "end" in data else datetime(2050),
            path=directory,
            problems=problems,
            users=users,
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
