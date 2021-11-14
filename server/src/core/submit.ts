import * as path from 'path';
import { ApiContext } from '../main/api-context';
import { Contest } from './contest';
import { evaluateSubmission } from './evaluate';
import { createFileFromContent, createFileFromPath } from './files/file-content';
import { Submission, SubmissionData, SubmissionInput } from './submission';
import { SubmissionFile } from './submission-file';
import { User } from './user';

export class Submit {
    static async submit(
        { contestId, problemName, username, files }: SubmissionInput,
        ctx: ApiContext,
        // Path of a local file to submit as solution (C++, C , Python only), used as a shortcut for the CLI
        // FIXME: improve the CLI to support multiple fields/file-types
        solutionPath?: string,
    ) {
        const contest = await new Contest(contestId, ctx).validate();
        await new User(contest, username, ctx).validate();

        const submissionData = await ctx.table(SubmissionData).create({ contestId: contest.id, problemName, username });
        const submission = Submission.fromId(submissionData.id, ctx);

        for (const { content, fieldName, fileName, fileTypeName } of files) {
            await ctx.table(SubmissionFile).create({
                fieldName,
                fileName,
                submissionId: submissionData.id,
                fileTypeName,
                contentId: (await createFileFromContent(ctx, Buffer.from(content.base64, 'base64'))).id,
            });
        }

        if (solutionPath !== undefined) {
            await ctx.table(SubmissionFile).create({
                submissionId: submissionData.id,
                fieldName: 'solution',
                fileTypeName: path.extname(solutionPath),
                fileName: path.basename(solutionPath),
                contentId: (await createFileFromPath(ctx, solutionPath)).id,
            });
        }

        evaluateSubmission(ctx, submission).catch(e => {
            console.error(`UNEXPECTED ERROR DURING EVALUATION:`);
            console.error(e);
        });

        return submission;
    }
}
