import pickle
import sys

from turingarena_common.commands import WorkingDirectory, Pack, GitRepository
from turingarena.api.request import CloudGenerateFileRequest

pickle.dump(CloudGenerateFileRequest(
    working_directory=WorkingDirectory(
        pack=Pack(
            oid="4f209f1b16bf778a8d678156aba6aae320f979c3",
            repository=GitRepository(
                url="https://github.com/turingarena/turingarena.git",
                branch=None,
                depth=None,
            ),
        ),
        current_directory="examples/sum_of_two_numbers",
    ),
), sys.stdout.buffer)
