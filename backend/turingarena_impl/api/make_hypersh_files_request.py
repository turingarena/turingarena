import pickle
import sys

from turingarena_common.commands import WorkingDirectory, Pack, GitCloneRepository
from turingarena_impl.api.request import CloudGenerateFilesRequest

pickle.dump(CloudGenerateFilesRequest(
    working_directory=WorkingDirectory(
        pack=Pack(
            parts=("d1a18623594c47621e9289767bc3ce997ce45756",),
            repositories=(
                GitCloneRepository(
                    url="https://github.com/turingarena/turingarena.git",
                    branch=None,
                    depth=None,
                ),
            )
        ),
        current_directory=".",
    ),
), sys.stdout.buffer)
