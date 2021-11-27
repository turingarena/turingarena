import { ApiContext } from '../main/api-context';
import { Contest } from './contest';
import { evaluateSubmission } from './evaluate';
import { Submission, SubmissionData, SubmissionInput } from './submission';
import { SubmissionItemData } from './submission-item';
import { User } from './user';

export async function submit({ contestId, problemName, username, files }: SubmissionInput, ctx: ApiContext) {
    const contest = await new Contest(contestId, ctx).validate();
    await new User(contest, username, ctx).validate();

    const submissionData = await ctx.table(SubmissionData).create({ contestId: contest.id, problemName, username });
    const submission = Submission.fromId(submissionData.id, ctx);

    for (const { content, fieldName, fileName, fileTypeName } of files) {
        // FIXME: check that file type name is allowed for this field
        await ctx.table(SubmissionItemData).create({
            fieldName,
            fileName,
            submissionId: submissionData.id,
            fileTypeName,
            fileContent: Buffer.from(content.base64, 'base64'),
        });
    }

    evaluateSubmission(ctx, submission).catch(e => {
        console.error(`UNEXPECTED ERROR DURING EVALUATION:`);
        console.error(e);
    });

    return submission;
}
