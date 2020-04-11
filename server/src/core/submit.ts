import * as path from 'path';
import { ApiContext } from '../main/api-context';
import { ModelRoot } from '../main/model-root';
import { Contest } from './contest';
import { EvaluateApi } from './evaluate';
import { FileContent } from './file-content';
import { Problem } from './problem';
import { Submission, SubmissionInput } from './submission';
import { SubmissionFile } from './submission-file';
import { User } from './user';

export async function submit(
    root: ModelRoot,
    { contestName, problemName, username, files }: SubmissionInput,
    // Path of a local file to submit as solution (C++ only), used as a shortcut for the CLI
    // FIXME: improve the CLI to support multiple fields/file-types
    solutionPath?: string,
) {
    const user = (await root.table(User).findOne({ where: { username } })) ?? root.fail(`no such user`);
    const problem =
        (await root.table(Problem).findOne({ where: { name: problemName } })) ?? root.fail(`no such problem`);
    const contest =
        (await root.table(Contest).findOne({ where: { name: contestName } })) ?? root.fail(`no such contest`);

    const submission = await root.table(Submission).create({
        contestId: contest.id,
        problemId: problem.id,
        userId: user.id,
    });

    for (const { content, fieldName, fileName, fileTypeName } of files) {
        await root.table(SubmissionFile).create({
            fieldName,
            fileName,
            submissionId: submission.id,
            fileTypeName,
            contentId: (await FileContent.createFromContent(root, Buffer.from(content.base64, 'base64'))).id,
        });
    }

    if (solutionPath !== undefined) {
        await root.table(SubmissionFile).create({
            submissionId: submission.id,
            fieldName: 'solution',
            fileTypeName: 'cpp',
            fileName: path.basename(solutionPath),
            contentId: (await FileContent.createFromPath(root, solutionPath)).id,
        });
    }

    // FIXME: merge with root
    const ctx = new ApiContext(root);
    ctx.api(EvaluateApi)
        .evaluate(submission)
        .catch(e => {
            console.error(`UNEXPECTED ERROR DURING EVALUATION:`);
            console.error(e);
        });
}
