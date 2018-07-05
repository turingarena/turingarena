import os
from tempfile import TemporaryDirectory

from turingarena_impl.api.dynamodb_submission import load_submission
from turingarena_impl.evaluation.evaluate import evaluate


def main():
    evaluator_cmd = os.environ["EVALUATOR_CMD"]
    submission_id = os.environ["SUBMISSION_ID"]

    files = load_submission(submission_id)

    for event in cloud_evaluate(files, evaluator_cmd):
        print(event)


def cloud_evaluate(files, evaluator_cmd):
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
            yield event


if __name__ == '__main__':
    main()
