import json
import os
import secrets
from io import StringIO

import boto3
from turingarena_common.commands import WorkingDirectory

from turingarena_impl.cli_server.pack import create_working_directory
from turingarena_impl.file.generated import PackGeneratedDirectory

S3_FILES_BUCKET = os.environ["S3_FILES_BUCKET"]


def generate_cloud_files(working_directory: WorkingDirectory):
    s3 = boto3.resource("s3")

    pack_id = secrets.token_hex(16)  # FIXME: should be the repo OID instead

    file_content = {}
    with create_working_directory(working_directory) as work_dir:
        generated = PackGeneratedDirectory(work_dir)
        for t, generator in generated.targets:
            file = StringIO()
            generator(file)
            file.seek(0)
            file_content[os.path.normpath(t)] = file.read()

        file_key = os.path.normpath(os.path.join(
            pack_id,
            working_directory.current_directory,
            "data.json",
        ))

    s3.Bucket(S3_FILES_BUCKET).put_object(
        ACL="public-read",
        Body=json.dumps(file_content),
        Key=file_key,
        StorageClass="REDUCED_REDUNDANCY",
    )
    url = s3.generate_presigned_url('get_object', Params=dict(
        Bucket=S3_FILES_BUCKET,
        Key=file_key,
    ))

    return url
