import * as path from 'path';
import { FileContent } from '../core/file-content';
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

    const participation = await ctx.db.Participation.findOne({ where: {
        userId: user.id,
        contestId: contest.id,
    }});

    if (participation === null) throw new Error(`user ${userName} not in contest ${contestName}`);

    const contestProblem = await ctx.db.ContestProblem.findOne({ where: {
        contestId: contest.id,
        problemId: problem.id,
    }});

    if (contestProblem === null) throw new Error(`problem ${problemName} not in contest ${contestName}`);

    const file = await FileContent.createFromPath(ctx, solutionPath);
    const submission = await ctx.db.Submission.create({
        participationId: participation.id,
        contestProblem: contestProblem.id,
    });

    await ctx.db.SubmissionFile.create({
        fieldId: 'solution',
        fileName: path.basename(solutionPath),
        submissionId: submission.id,
        fileId: file.id,
    });

    await submission.extract('/tmp/xxx');
}
