import base64
import json
import os
from tempfile import TemporaryDirectory

import boto3

from turingarena_impl.api.aws_backend import SubmissionFile
from turingarena_impl.evaluation.evaluate import evaluate


def main():
    evaluator_cmd = os.environ["EVALUATOR_CMD"]
    submission_id = os.environ["SUBMISSION_ID"]

    dynamodb = boto3.client("dynamodb")
    response = dynamodb.get_item(
        TableName='SubmissionsTable',
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

    with TemporaryDirectory() as temp_dir:
        file_paths = {}
        for name, file in files.items():
            dir_name = os.path.join(temp_dir, name)
            os.mkdir(dir_name)
            filename = os.path.join(dir_name, file.filename)
            with open(filename, "xb") as f:
                f.write(file.content)
            file_paths[name] = filename

        for event in evaluate(file_paths, evaluator_cmd=evaluator_cmd):
            print(event)


if __name__ == '__main__':
    main()
