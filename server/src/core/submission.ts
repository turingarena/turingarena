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
import { __generated_SubmissionInput } from '../generated/graphql-types';
import { BaseModel } from '../main/base-model';
import { Resolvers } from '../main/resolver-types';
import { Contest } from './contest';
import { ContestProblemAssignment } from './contest-problem-assignment';
import { Evaluation, EvaluationStatus } from './evaluation';
import { FulfillmentGradeDomain } from './feedback/fulfillment';
import { ScoreGrade, ScoreGradeDomain } from './feedback/score';
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

        summaryRow: Record!
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
            (await this.root.table(ContestProblemAssignment).findOne({
                where: { contestId: this.contestId, problemId: this.problemId },
            })) ?? this.root.fail()
        );
    }

    async getParticipation(): Promise<Participation> {
        return (
            (await this.root.table(Participation).findOne({
                where: { contestId: this.contestId, userId: this.userId },
            })) ?? this.root.fail()
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

    async getOfficialEvaluation() {
        return this.root.table(Evaluation).findOne({
            where: { submissionId: this.id },
            order: [['createdAt', 'DESC']],
        });
    }

    async getMaterial() {
        return (await this.getProblem()).getMaterial();
    }

    async getAwardAchievements() {
        const evaluation = await this.getOfficialEvaluation();
        const achievements = (await evaluation?.getAchievements()) ?? [];

        return (await this.getMaterial()).awards.map((award, awardIndex) => ({
            award,
            achievement: achievements.find(a => a.awardIndex === awardIndex),
        }));
    }

    async getTotalScore() {
        if ((await this.getOfficialEvaluation())?.status !== EvaluationStatus.SUCCESS) return undefined;

        return ScoreGrade.total(
            (await this.getAwardAchievements()).flatMap(({ achievement, award: { gradeDomain } }) => {
                if (gradeDomain instanceof ScoreGradeDomain && achievement !== undefined) {
                    return [achievement.getScoreGrade(gradeDomain)];
                }

                return [];
            }),
        );
    }

    async getSummaryRow() {
        const fields = [
            ...(await this.getAwardAchievements()).map(({ award: { gradeDomain }, achievement }) => {
                if (gradeDomain instanceof ScoreGradeDomain) {
                    return {
                        __typename: 'ScoreField',
                        score: achievement?.getScoreGrade(gradeDomain)?.score ?? null,
                        scoreRange: gradeDomain.scoreRange,
                    };
                }
                if (gradeDomain instanceof FulfillmentGradeDomain) {
                    return {
                        __typename: 'FulfillmentField',
                        fulfilled: achievement?.getFulfillmentGrade()?.fulfilled ?? null,
                    };
                }
                throw new Error(`unexpected grade domain ${gradeDomain}`);
            }),
            {
                __typename: 'ScoreField',
                score: (await this.getTotalScore())?.score,
                scoreRange: (await (await this.getProblem()).getMaterial()).scoreRange,
            },
        ];

        return { __typename: 'Record', fields };
    }
}

export interface SubmissionModelRecord {
    Submission: Submission;
}

export type SubmissionInput = __generated_SubmissionInput;

export const submissionResolvers: Resolvers = {
    Submission: {
        contest: submission => submission.getContest(),
        user: submission => submission.getUser(),
        problem: submission => submission.getProblem(),

        participation: submission => submission.getParticipation(),
        contestProblemAssigment: submission => submission.getContestProblemAssignment(),

        officialEvaluation: submission => submission.getOfficialEvaluation(),
        summaryRow: submission => submission.getSummaryRow(),
    },
};
