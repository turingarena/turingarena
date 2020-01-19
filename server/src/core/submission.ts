import { gql } from 'apollo-server-core';
import * as path from 'path';
import { AllowNull, BelongsTo, Column, ForeignKey, HasMany, Model, Table } from 'sequelize-typescript';
import { Contest } from './contest';
import { ContestProblem } from './contest-problem';
import { Evaluation } from './evaluation';
import { Participation } from './participation';
import { Problem } from './problem';
import { SubmissionFile } from './submission-file';

export const submissionSchema = gql`
    type Submission {
        id: ID!
        problem: Problem!
        user: User!
        contest: Contest!
        files: [SubmissionFile!]!
        createdAt: String!
        officialEvaluation: Evaluation!
        evaluations: [Evaluation!]!
    }

    type SubmissionFile {
        fieldId: ID!
        content: FileContent!
    }

    input SubmissionInput {
        problemName: ID!
        contestName: ID!
        username: ID!
        files: [SubmissionFileInput!]!
    }

    input SubmissionFileInput {
        fieldId: ID!
        file: FileInput!
    }

    type Evaluation {
        submission: Submission!
        events: [EvaluationEvent!]!
    }

    type EvaluationEvent {
        evaluation: Evaluation!
        data: String!
    }
`;

/** A Submission in the system */
@Table({ updatedAt: false })
export class Submission extends Model<Submission> {
    @ForeignKey(() => Problem)
    @AllowNull(false)
    @Column
    contestProblemId!: number;

    @ForeignKey(() => Participation)
    @AllowNull(false)
    @Column
    participationId!: number;

    /** Files of this submission */
    @HasMany(() => SubmissionFile)
    submissionFiles!: SubmissionFile[];
    getSubmissionFiles!: () => Promise<SubmissionFile[]>;

    /** Evaluations of this submission */
    @HasMany(() => Evaluation)
    evaluations!: Evaluation[];

    /** ContestProblem to which this submission belongs to */
    @BelongsTo(() => ContestProblem, 'contestProblemId')
    contestProblem!: ContestProblem;
    getContestProblem!: (options?: object) => Promise<ContestProblem>;

    /** User that made this submission */
    @BelongsTo(() => Participation, 'participationId')
    participation!: Participation;
    getParticipation!: (options?: object) => Promise<Participation>;

    /**
     * Extract the files of this submission in the specified base dir.
     * It extract files as: `${base}/${file.fieldId}/${file.path}.
     *
     * @param base base directory
     */
    async extract(base: string) {
        const submissionFiles = await this.getSubmissionFiles();

        for (const submissionFile of submissionFiles) {
            const content = await submissionFile.getFile();
            const filePath = path.join(base, submissionFile.fieldId, submissionFile.fileName);
            await content.extract(filePath);
        }
    }
}
