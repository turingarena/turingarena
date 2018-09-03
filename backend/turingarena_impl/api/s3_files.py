import os
from io import StringIO

import boto3

from turingarena_common.commands import WorkingDirectory
from turingarena_impl.cli_server.pack import create_working_directory
from turingarena_impl.file.generated import PackGeneratedDirectory


def generate_cloud_files(working_directory: WorkingDirectory):
    s3 = boto3.resource("s3")

    pack_id = "_".join(working_directory.pack.parts)

    with create_working_directory(working_directory) as work_dir:
        generated = PackGeneratedDirectory(work_dir)
        for t, generator in generated.targets:
            file = StringIO()
            generator(file)
            file.seek(0)

            s3.Bucket("turingarena-files-bucket").put_object(
                ACL="public-read",
                Body=file.read().encode(),
                Key=f"{pack_id}/{os.path.normpath(t)}",
                StorageClass="REDUCED_REDUNDANCY",
            )
