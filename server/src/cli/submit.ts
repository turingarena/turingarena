import * as path from 'path';
import { Contest } from '../core/contest';
import { evaluate } from '../core/evaluate';
import { FileContent } from '../core/file-content';
import { Problem } from '../core/problem';
import { Submission } from '../core/submission';
import { SubmissionFile } from '../core/submission-file';
import { User } from '../core/user';
import { ApiContext } from '../main/context';

/**
 * Inserts a submission in the database
 *
 * @param ctx Context
 * @param userName Username that submits
 * @param contestName Contest name to submit to
 * @param problemName Problem name to submit
 * @param solutionPath Path of the submission file
 */
export async function createSubmission(
    ctx: ApiContext,
    userName: string,
    contestName: string,
    problemName: string,
    solutionPath: string,
) {
    const user = await ctx.table(User).findOne({ where: { username: userName } });
    const problem = await ctx.table(Problem).findOne({
        where: { name: problemName },
    });
    const contest = await ctx.table(Contest).findOne({
        where: { name: contestName },
    });

    if (contest === null) throw new Error(`contest does not exist`);
    if (user === null) throw new Error(`user does not exist`);
    if (problem === null) throw new Error(`problem does not exist`);

    const file = await FileContent.createFromPath(ctx, solutionPath);
    const submission = await ctx.table(Submission).create({
        contestId: contest.id,
        problemId: problem.id,
        userId: user.id,
    });

    await ctx.table(SubmissionFile).create({
        fieldId: 'solution',
        fileName: path.basename(solutionPath),
        submissionId: submission.id,
        fileId: file.id,
    });

    await evaluate(ctx, submission);
}
