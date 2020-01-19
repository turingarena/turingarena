import { gql } from 'apollo-server-core';
import * as path from 'path';
import { AllowNull, BelongsTo, Column, ForeignKey, HasMany, Model, Table } from 'sequelize-typescript';
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
            const content = await submissionFile.getFile();
            const filePath = path.join(base, this.id as string, submissionFile.fieldId, submissionFile.fileName);
            await content.extract(filePath);
        }
    }
}
