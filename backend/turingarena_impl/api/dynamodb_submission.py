import base64
import json
import os
import time

import boto3

from turingarena_common.submission import SubmissionFile


DYNAMODB_SUBMISSIONS_TABLE = os.environ['DYNAMODB_SUBMISSIONS_TABLE']


def save_submission(id, files):
    submission_json = dict(
        files={
            name: dict(
                filename=file_data.filename,
                content=base64.b64encode(file_data.content).decode()
            )
            for name, file_data in files.items()
        }
    )

    dynamodb = boto3.client("dynamodb")
    dynamodb.put_item(
        TableName=DYNAMODB_SUBMISSIONS_TABLE,
        Item={
            'id': {
                'S': id,
            },
            'expires': {
                'N': str(int(time.time() + 10 * 60)),
            },
            'data': {
                'S': json.dumps(submission_json),
            }
        },
    )


def load_submission(submission_id):
    dynamodb = boto3.client("dynamodb")
    response = dynamodb.get_item(
        TableName=DYNAMODB_SUBMISSIONS_TABLE,
        Key={
            'id': {
                'S': submission_id,
            },
        },
    )
    if 'Item' not in response:
        raise ValueError(f"submission not found: '{submission_id}'")
    data = json.loads(response['Item']['data']['S'])
    files = {
        name: SubmissionFile(
            filename=file_data["filename"],
            content=base64.b64decode(file_data["content"]),
        )
        for name, file_data in data["files"].items()
    }
    return files
