import * as fs from 'fs';
import * as path from 'path';
import { ApiContext } from '../api';
import { File } from '../model/file';

/**
 * Inserts a submission in the database
 *
 * @param ctx Context
 * @param userName Username that submits
 * @param contestName Contest name to submit to
 * @param problemName Problem name to submit
 * @param solutionPath Path of the submission file
 */
export async function createSubmission(ctx: ApiContext, userName, contestName, problemName, solutionPath) {
    const user = await ctx.db.User.findOne({ where: { username: userName } });
    const problem = await ctx.db.Problem.findOne({ where: { name: problemName } });
    const contest = await ctx.db.Contest.findOne({ where: { name: contestName } });

    const file = await File.createFromPath(ctx, solutionPath);
    const submission = await ctx.db.Submission.create({
        userId: user.id,
        contestId: contest.id,
        problemId: problem.id,
    });

    const submissionFile = await ctx.db.SubmissionFile.create({
        fieldId: 'solution',
        fileName: path.basename(solutionPath),
        submissionId: submission.id,
        fileId: file.id,
    });

    await submission.extract('/tmp/xxx');
}
