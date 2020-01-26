import { gql } from 'apollo-server-core';
import * as path from 'path';
import {
    AllowNull,
    AutoIncrement,
    BelongsTo,
    Column,
    ForeignKey,
    HasMany,
    PrimaryKey,
    Table,
} from 'sequelize-typescript';
import { FindOptions } from 'sequelize/types';
import { BaseModel } from '../main/base-model';
import { ResolversWithModels } from '../main/resolver-types';
import { Contest } from './contest';
import { ContestProblemAssignment } from './contest-problem-assignment';
import { Evaluation } from './evaluation';
import { Participation } from './participation';
import { Problem } from './problem';
import { SubmissionFile } from './submission-file';
import { User } from './user';

export const submissionSchema = gql`
    type Submission {
        id: ID!

        problem: Problem!
        user: User!
        contest: Contest!

        contestProblemAssigment: ContestProblemAssignment!
        participation: Participation!

        files: [SubmissionFile!]!
        createdAt: String!
        officialEvaluation: Evaluation
        evaluations: [Evaluation!]!
    }

    input SubmissionInput {
        problemName: ID!
        contestName: ID!
        username: ID!
        files: [SubmissionFileInput!]!
    }
`;

/** A Submission in the system */
@Table({ updatedAt: false })
export class Submission extends BaseModel<Submission> {
    @PrimaryKey
    @AutoIncrement
    @Column
    id!: number;

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
    getEvaluations!: (options?: FindOptions) => Promise<Evaluation[]>;

    /** Problem to which this submission belongs to */
    @BelongsTo(() => Problem)
    problem!: Problem;
    getProblem!: (options?: object) => Promise<Problem>;

    /** Problem to which this submission belongs to */
    @BelongsTo(() => Contest)
    contest!: Contest;
    getContest!: (options?: object) => Promise<Contest>;

    /** Problem to which this submission belongs to */
    @BelongsTo(() => User)
    user!: User;
    getUser!: (options?: object) => Promise<User>;

    async getContestProblemAssignment(): Promise<ContestProblemAssignment> {
        return (
            (await this.modelRoot.table(ContestProblemAssignment).findOne({
                where: { contestId: this.contestId, problemId: this.problemId },
            })) ?? this.modelRoot.fail()
        );
    }

    async getParticipation(): Promise<Participation> {
        return (
            (await this.modelRoot.table(Participation).findOne({
                where: { contestId: this.contestId, userId: this.userId },
            })) ?? this.modelRoot.fail()
        );
    }

    /**
     * Extract the files of this submission in the specified base dir.
     * It extract files as: `${base}/${submissionId}/${fieldName}.${fileTypeName}${extension}`
     *
     * @param base base directory
     */
    async extract(base: string) {
        const submissionFiles = await this.getSubmissionFiles();

        const submissionPath = path.join(base, this.id.toString());

        for (const submissionFile of submissionFiles) {
            const content = await submissionFile.getContent({ attributes: ['id', 'content'] });
            const { fieldName, fileTypeName } = submissionFile;

            const extension = '.cpp'; // FIXME: determine extension from file type

            const filePath = path.join(submissionPath, `${fieldName}.${fileTypeName}${extension}`);
            await content.extract(filePath);
        }

        return submissionPath;
    }
}

export const submissionResolvers: ResolversWithModels<{
    Submission: Submission;
}> = {
    Submission: {
        contest: submission => submission.getContest(),
        user: submission => submission.getUser(),
        problem: submission => submission.getProblem(),

        participation: submission => submission.getParticipation(),
        contestProblemAssigment: submission => submission.getContestProblemAssignment(),

        officialEvaluation: submission =>
            submission.modelRoot.table(Evaluation).findOne({
                where: { submissionId: submission.id },
                order: [['createdAt', 'DESC']],
            }),
    },
};
