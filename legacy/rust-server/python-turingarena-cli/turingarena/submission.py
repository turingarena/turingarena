from __future__ import annotations

import base64
import json
import os

from datetime import datetime
from dataclasses import dataclass
from typing import List


@dataclass
class SubmissionFile:
    name: str
    field_id: str
    type_id: str
    content: bytes

    @staticmethod
    def from_graphql(data: dict) -> SubmissionFile:
        return SubmissionFile(
            name=data["name"],
            field_id=data["fieldId"],
            type_id=data["typeId"],
            content=base64.standard_b64decode(data["content"]["base64"]),
        )

    @staticmethod
    def from_file(file_path: str):
        with open(file_path, "rb") as f:
            content = f.read()

        return SubmissionFile(
            name=os.path.basename(file_path),
            type_id="cpp",  # TODO: identify correct file type
            field_id="solution",
            content=content,
        )

    def to_graphql(self) -> dict:
        return dict(
            name=self.name,
            fieldId=self.field_id,
            typeId=self.type_id,
            content=dict(base64=base64.standard_b64encode(self.content).decode("utf-8")),
        )

    def write(self, directory: str):
        with open(os.path.join(directory, self.name), "wb") as f:
            f.write(self.content)


@dataclass
class Evaluation:
    id: str
    status: str
    # TODO: missing fields

    @staticmethod
    def from_graphql(data: dict) -> Evaluation:
        return Evaluation(
            id=data["id"],
            status=data["status"],
        )

    def to_dict(self) -> dict:
        return dict(
            id=self.id,
            status=self.status,
        )

    def write(self, directory: str):
        with open(os.path.join(directory, "evaluation.json"), "w") as f:
            json.dump(self.to_dict(), f)


@dataclass
class Submission:
    id: str
    user: str
    created_at: datetime
    problem: str
    evaluation: Evaluation
    files: List[SubmissionFile]

    @staticmethod
    def from_graphql(data: dict) -> Submission:
        return Submission(
            id=data["id"],
            user=data["userId"],
            created_at=datetime.strptime(data["createdAt"].split(".")[0], "%Y-%m-%dT%H:%M:%S"), # TODO: Rust output strange dates...
            problem=data["problem"]["name"],
            files=list(map(lambda f: SubmissionFile.from_graphql(f), data["files"])),
            evaluation=Evaluation.from_graphql(data["evaluation"])
        )

    def path(self, base):
        return os.path.join(base, self.problem, self.user, self.created_at.isoformat())

    def write(self, base: str):
        directory = self.path(base)
        os.makedirs(directory, exist_ok=True)
        self.evaluation.write(directory)
        for file in self.files:
            file.write(directory)


