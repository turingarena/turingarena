import * as path from 'path';
import { File } from '../core/file';
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
    userName,
    contestName,
    problemName,
    solutionPath,
) {
    const user = await ctx.db.User.findOne({ where: { username: userName } });
    const problem = await ctx.db.Problem.findOne({
        where: { name: problemName },
    });
    const contest = await ctx.db.Contest.findOne({
        where: { name: contestName },
    });

    if (contest === null) throw new Error(`contest does not exist`);
    if (user === null) throw new Error(`user does not exist`);
    if (problem === null) throw new Error(`problem does not exist`);

    const file = await File.createFromPath(ctx, solutionPath);
    const submission = await ctx.db.Submission.create({
        userId: user.id,
        contestId: contest.id,
        problemId: problem.id,
    });

    // const submissionFile =
    await ctx.db.SubmissionFile.create({
        fieldId: 'solution',
        fileName: path.basename(solutionPath),
        submissionId: submission.id,
        fileId: file.id,
    });

    await submission.extract('/tmp/xxx');
}
