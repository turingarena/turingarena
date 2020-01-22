import { gql } from 'apollo-server-core';
import * as path from 'path';
import { AllowNull, BelongsTo, Column, ForeignKey, HasMany, Table } from 'sequelize-typescript';
import { BaseModel } from '../main/base-model';
import { Contest } from './contest';
import { Evaluation } from './evaluation';
import { Problem } from './problem';
import { SubmissionFile } from './submission-file';
import { User } from './user';

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

    input SubmissionInput {
        problemName: ID!
        contestName: ID!
        username: ID!
        files: [SubmissionFileInput!]!
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
export class Submission extends BaseModel<Submission> {
    @ForeignKey(() => Problem)
    @AllowNull(false)
    @Column
    problemId!: number;

    @ForeignKey(() => Contest)
    @AllowNull(false)
    @Column
    contestId!: number;

    @ForeignKey(() => User)
    @AllowNull(false)
    @Column
    userId!: number;

    /** Files of this submission */
    @HasMany(() => SubmissionFile)
    submissionFiles!: SubmissionFile[];
    getSubmissionFiles!: () => Promise<SubmissionFile[]>;

    /** Evaluations of this submission */
    @HasMany(() => Evaluation)
    evaluations!: Evaluation[];

    /** Problem to which this submission belongs to */
    @BelongsTo(() => Problem)
    problem!: Problem;
    getProblem!: (options?: object) => Promise<Problem>;

    /**
     * Extract the files of this submission in the specified base dir.
     * It extract files as: `${base}/${submissionId}/${fieldId}/${fileName}.
     *
     * @param base base directory
     */
    async extract(base: string) {
        const submissionFiles = await this.getSubmissionFiles();

        for (const submissionFile of submissionFiles) {
            const content = await submissionFile.getContent();
            const filePath = path.join(
                base,
                (this.id as number).toString(),
                submissionFile.fieldName,
                submissionFile.fileName,
            );
            await content.extract(filePath);
        }
    }
}
