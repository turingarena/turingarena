import { gql } from 'apollo-server-core';
import * as path from 'path';
import { AllowNull, BelongsTo, Column, ForeignKey, HasMany, Table } from 'sequelize-typescript';
import { FindOptions } from 'sequelize/types';
import { __generated_SubmissionInput } from '../generated/graphql-types';
import { ApiObject } from '../main/api';
import { createByIdLoader, createSimpleLoader, UuidBaseModel } from '../main/base-model';
import { Resolvers } from '../main/resolver-types';
import { AchievementApi } from './achievement';
import { Contest, ContestApi } from './contest';
import { ContestProblemAssignment, ContestProblemAssignmentApi } from './contest-problem-assignment';
import { Evaluation, EvaluationStatus } from './evaluation';
import { FulfillmentGradeDomain } from './feedback/fulfillment';
import { ScoreGrade, ScoreGradeDomain } from './feedback/score';
import { ParticipationApi } from './participation';
import { Problem, ProblemApi } from './problem';
import { SubmissionFile } from './submission-file';
import { User, UserApi } from './user';

export const submissionSchema = gql`
    type Submission {
        id: ID!

        problem: Problem!
        user: User!
        contest: Contest!

        contestProblemAssigment: ContestProblemAssignment!
        participation: Participation!

        files: [SubmissionFile!]!
        createdAt: DateTime!
        officialEvaluation: Evaluation
        evaluations: [Evaluation!]!

        summaryRow: Record!
        feedbackTable: FeedbackTable!
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
export class Submission extends UuidBaseModel<Submission> {
    @ForeignKey(() => Problem)
    @AllowNull(false)
    @Column
    problemId!: string;

    @ForeignKey(() => Contest)
    @AllowNull(false)
    @Column
    contestId!: string;

    @ForeignKey(() => User)
    @AllowNull(false)
    @Column
    userId!: string;

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
}

export interface SubmissionModelRecord {
    Submission: Submission;
}

export type SubmissionInput = __generated_SubmissionInput;

export class SubmissionApi extends ApiObject {
    byId = createByIdLoader(this.ctx, Submission);
    allByTackling = createSimpleLoader(
        ({ problemId, contestId, userId }: { problemId: string; contestId: string; userId: string }) =>
            this.ctx.root
                .table(Submission)
                .findAll({ where: { problemId, contestId, userId }, order: [['createdAt', 'ASC']] }),
    );

    async getContestProblemAssignment(s: Submission): Promise<ContestProblemAssignment> {
        return this.ctx
            .api(ContestProblemAssignmentApi)
            .byContestAndProblem.load({ contestId: s.contestId, problemId: s.problemId });
    }

    /**
     * Extract the files of this submission in the specified base dir.
     * It extract files as: `${base}/${submissionId}/${fieldName}.${fileTypeName}${extension}`
     *
     * @param base base directory
     */
    async extract(s: Submission, base: string) {
        const submissionFiles = await s.getSubmissionFiles();
        const submissionPath = path.join(base, s.id);

        for (const submissionFile of submissionFiles) {
            const content = await submissionFile.getContent({ attributes: ['id', 'content'] });
            const { fieldName, fileTypeName } = submissionFile;

            const extension = '.cpp'; // FIXME: determine extension from file type

            const filePath = path.join(submissionPath, `${fieldName}.${fileTypeName}${extension}`);
            await content.extract(filePath);
        }

        return submissionPath;
    }

    async getOfficialEvaluation(s: Submission) {
        return this.ctx.root.table(Evaluation).findOne({
            where: { submissionId: s.id },
            order: [['createdAt', 'DESC']],
        });
    }

    async getProblem(s: Submission) {
        return this.ctx.api(ProblemApi).byId.load(s.problemId);
    }

    async getMaterial(s: Submission) {
        const problem = await this.getProblem(s);

        return problem.getMaterial();
    }

    async getAwardAchievements(s: Submission) {
        const evaluation = await this.getOfficialEvaluation(s);
        const achievements = (await evaluation?.getAchievements()) ?? [];
        const material = await this.getMaterial(s);

        return material.awards.map((award, awardIndex) => ({
            award,
            achievement: achievements.find(a => a.awardIndex === awardIndex),
        }));
    }

    async getTotalScore(s: Submission) {
        if ((await this.getOfficialEvaluation(s))?.status !== EvaluationStatus.SUCCESS) return undefined;

        return ScoreGrade.total(
            (await this.getAwardAchievements(s)).flatMap(({ achievement, award: { gradeDomain } }) => {
                if (gradeDomain instanceof ScoreGradeDomain && achievement !== undefined) {
                    return [this.ctx.api(AchievementApi).getScoreGrade(achievement, gradeDomain)];
                }

                return [];
            }),
        );
    }

    async getSummaryRow(s: Submission) {
        return {
            __typename: 'Record',
            fields: [
                ...(await this.getAwardAchievements(s)).map(({ award: { gradeDomain }, achievement }) => {
                    if (gradeDomain instanceof ScoreGradeDomain) {
                        return {
                            __typename: 'ScoreField',
                            score:
                                achievement !== undefined
                                    ? this.ctx.api(AchievementApi).getScoreGrade(achievement, gradeDomain)?.score
                                    : null,
                            scoreRange: gradeDomain.scoreRange,
                        };
                    }
                    if (gradeDomain instanceof FulfillmentGradeDomain) {
                        return {
                            __typename: 'FulfillmentField',
                            fulfilled:
                                achievement !== undefined
                                    ? this.ctx.api(AchievementApi).getFulfillmentGrade(achievement)
                                    : null,
                        };
                    }
                    throw new Error(`unexpected grade domain ${gradeDomain}`);
                }),
                {
                    __typename: 'ScoreField',
                    score: (await this.getTotalScore(s))?.score,
                    scoreRange: (await this.getMaterial(s)).scoreRange,
                },
            ],
        };
    }

    async getFeedbackTable(s: Submission) {
        const { awards, taskInfo, evaluationFeedbackColumns } = await this.getMaterial(s);
        const { scoring, limits } = taskInfo.IOI;

        const limitsMarginMultiplier = 2;
        const memoryUnitBytes = 1024;
        const memoryLimitUnitMultiplier = 1024;
        const warningWatermarkMultiplier = 0.2;

        const evaluation = await this.getOfficialEvaluation(s);
        const events = (await evaluation?.getEvents()) ?? [];

        const testCasesData = awards.flatMap((award, awardIndex) =>
            new Array(scoring.subtasks[awardIndex].testcases).fill(0).map(() => ({
                award,
                awardIndex,
                timeUsage: null as number | null,
                memoryUsage: null as number | null,
                message: null as string | null,
                score: null as number | null,
            })),
        );

        for (const { data } of events) {
            if ('IOITestcaseScore' in data) {
                const { testcase, score, message } = data.IOITestcaseScore;
                const testCaseData = testCasesData[testcase];
                testCaseData.message = message;
                testCaseData.score = score;
            }

            if ('IOIEvaluation' in data) {
                const { status, testcase } = data.IOIEvaluation;
                if (status.Done !== undefined) {
                    const { cpu_time, memory } = status.Done.result.resources;
                    const testCaseData = testCasesData[testcase];
                    testCaseData.memoryUsage = memory;
                    testCaseData.timeUsage = cpu_time;
                }
            }
        }

        return {
            __typename: 'FeedbackTable',
            columns: evaluationFeedbackColumns,
            rows: testCasesData.map(({ awardIndex, score, message, timeUsage, memoryUsage }, testCaseIndex) => ({
                fields: [
                    {
                        __typename: 'IndexField',
                        index: awardIndex,
                    },
                    {
                        __typename: 'IndexField',
                        index: testCaseIndex,
                    },
                    {
                        __typename: 'TimeUsageField',
                        timeUsage: timeUsage !== null ? { seconds: timeUsage } : null,
                        timeUsageMaxRelevant: { seconds: limits.time * limitsMarginMultiplier },
                        timeUsagePrimaryWatermark: { seconds: limits.time },
                        valence:
                            timeUsage === null
                                ? null
                                : timeUsage <= warningWatermarkMultiplier * limits.time
                                ? 'NOMINAL'
                                : timeUsage <= limits.time
                                ? 'WARNING'
                                : 'FAILURE',
                    },
                    {
                        __typename: 'MemoryUsageField',
                        memoryUsage: memoryUsage !== null ? { bytes: memoryUsage * memoryUnitBytes } : null,
                        memoryUsageMaxRelevant: {
                            bytes: memoryUnitBytes * limits.memory * memoryLimitUnitMultiplier * limitsMarginMultiplier,
                        },
                        memoryUsagePrimaryWatermark: {
                            bytes: memoryUnitBytes * limits.memory * memoryLimitUnitMultiplier,
                        },
                        valence:
                            memoryUsage === null
                                ? null
                                : memoryUsage <= warningWatermarkMultiplier * limits.memory * memoryLimitUnitMultiplier
                                ? 'NOMINAL'
                                : memoryUsage <= limits.memory * memoryLimitUnitMultiplier
                                ? 'WARNING'
                                : 'FAILURE',
                    },
                    {
                        __typename: 'MessageField',
                        message: message !== null ? [{ value: message }] : null,
                    },
                    {
                        __typename: 'ScoreField',
                        score,
                        scoreRange: {
                            max: 1,
                            decimalDigits: 2,
                            allowPartial: true,
                        },
                    },
                ],
            })),
        };
    }
}

export const submissionResolvers: Resolvers = {
    Submission: {
        id: s => s.id,

        contest: (s, {}, ctx) => ctx.api(ContestApi).byId.load(s.contestId),
        user: (s, {}, ctx) => ctx.api(UserApi).byUsername.load(s.userId),
        problem: (s, {}, ctx) => ctx.api(ProblemApi).byId.load(s.problemId),

        participation: ({ userId, contestId }, {}, ctx) =>
            ctx.api(ParticipationApi).byUserAndContest.load({ contestId, userId }),
        contestProblemAssigment: ({ contestId, problemId }, {}, ctx) =>
            ctx.api(ContestProblemAssignmentApi).byContestAndProblem.load({ contestId, problemId }),

        officialEvaluation: (s, {}, ctx) => ctx.api(SubmissionApi).getOfficialEvaluation(s),
        summaryRow: (s, {}, ctx) => ctx.api(SubmissionApi).getSummaryRow(s),
        feedbackTable: (s, {}, ctx) => ctx.api(SubmissionApi).getFeedbackTable(s),

        createdAt: s => s.createdAt,
        evaluations: s => s.evaluations,
        files: s => s.submissionFiles,
    },
};
