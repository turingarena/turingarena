import * as path from 'path';
import { ApiObject } from '../main/api';
import { ContestApi } from './contest';
import { EvaluateApi } from './evaluate';
import { FileContentApi } from './files/file-content';
import { Submission, SubmissionInput } from './submission';
import { SubmissionFile } from './submission-file';
import { UserApi } from './user';

export class SubmitApi extends ApiObject {
    async submit(
        { contestId, problemName, username, files }: SubmissionInput,
        // Path of a local file to submit as solution (C++ only), used as a shortcut for the CLI
        // FIXME: improve the CLI to support multiple fields/file-types
        solutionPath?: string,
    ) {
        const contest = await this.ctx.api(ContestApi).validate({ __typename: 'Contest', id: contestId });
        await this.ctx.api(UserApi).validate({ __typename: 'User', contest, username });

        const submission = await this.ctx.table(Submission).create({ contestId: contest.id, problemName, username });

        for (const { content, fieldName, fileName, fileTypeName } of files) {
            await this.ctx.table(SubmissionFile).create({
                fieldName,
                fileName,
                submissionId: submission.id,
                fileTypeName,
                contentId: (await this.ctx.api(FileContentApi).createFromContent(Buffer.from(content.base64, 'base64')))
                    .id,
            });
        }

        if (solutionPath !== undefined) {
            await this.ctx.table(SubmissionFile).create({
                submissionId: submission.id,
                fieldName: 'solution',
                fileTypeName: 'cpp',
                fileName: path.basename(solutionPath),
                contentId: (await this.ctx.api(FileContentApi).createFromPath(solutionPath)).id,
            });
        }

        this.ctx
            .api(EvaluateApi)
            .evaluate(submission)
            .catch(e => {
                console.error(`UNEXPECTED ERROR DURING EVALUATION:`);
                console.error(e);
            });

        return submission;
    }
}
