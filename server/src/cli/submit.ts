import * as path from 'path';
import { Contest } from '../core/contest';
import { evaluate } from '../core/evaluate';
import { FileContent } from '../core/file-content';
import { Problem } from '../core/problem';
import { Submission } from '../core/submission';
import { SubmissionFile } from '../core/submission-file';
import { User } from '../core/user';
import { ModelRoot } from '../main/model-root';

/**
 * Inserts a submission in the database
 *
 * @param root Context
 * @param userName Username that submits
 * @param contestName Contest name to submit to
 * @param problemName Problem name to submit
 * @param solutionPath Path of the submission file
 */
export async function createSubmission(
    root: ModelRoot,
    userName: string,
    contestName: string,
    problemName: string,
    solutionPath: string,
) {
    const user = await root.table(User).findOne({ where: { username: userName } });
    const problem = await root.table(Problem).findOne({
        where: { name: problemName },
    });
    const contest = await root.table(Contest).findOne({
        where: { name: contestName },
    });

    if (contest === null) throw new Error(`contest does not exist`);
    if (user === null) throw new Error(`user does not exist`);
    if (problem === null) throw new Error(`problem does not exist`);

    const file = await FileContent.createFromPath(root, solutionPath);
    const submission = await root.table(Submission).create({
        contestId: contest.id,
        problemId: problem.id,
        userId: user.id,
    });

    await root.table(SubmissionFile).create({
        fieldId: 'solution',
        fileName: path.basename(solutionPath),
        submissionId: submission.id,
        fileId: file.id,
    });

    await evaluate(root, submission);
}
