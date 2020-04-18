import { gql } from 'apollo-server-core';
import * as path from 'path';
import { AllowNull, Column, ForeignKey, Table } from 'sequelize-typescript';
import { __generated_SubmissionInput } from '../generated/graphql-types';
import { ApiObject } from '../main/api';
import { createByIdDataLoader, createSimpleLoader, UuidBaseModel } from '../main/base-model';
import { Resolvers } from '../main/resolver-types';
import { AchievementApi } from './achievement';
import { ContestApi, ContestData } from './contest';
import { ContestProblemAssignment } from './contest-problem-assignment';
import { Evaluation, EvaluationApi, EvaluationStatus } from './evaluation';
import { EvaluationEventApi } from './evaluation-event';
import { FulfillmentGradeDomain } from './feedback/fulfillment';
import { ScoreGrade, ScoreGradeDomain } from './feedback/score';
import { FileContentApi } from './files/file-content';
import { ProblemMaterialApi } from './material/problem-material';
import { Participation } from './participation';
import { Problem } from './problem';
import { SubmissionFileApi } from './submission-file';
import { UserApi } from './user';

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
        contestId: ID!
        problemName: ID!
        username: ID!
        files: [SubmissionFileInput!]!
    }
`;

/** A Submission in the system */
@Table({ updatedAt: false })
export class Submission extends UuidBaseModel<Submission> {
    @ForeignKey(() => ContestData)
    @AllowNull(false)
    @Column
    contestId!: string;

    @AllowNull(false)
    @Column
    problemName!: string;

    @AllowNull(false)
    @Column
    username!: string;
}

export interface SubmissionModelRecord {
    Submission: Submission;
}

export type SubmissionInput = __generated_SubmissionInput;

export class SubmissionApi extends ApiObject {
    byId = createByIdDataLoader(this.ctx, Submission);
    allByTackling = createSimpleLoader(
        ({ problemName, contestId, username }: { problemName: string; contestId: string; username: string }) =>
            this.ctx
                .table(Submission)
                .findAll({ where: { problemName, contestId, username }, order: [['createdAt', 'ASC']] }),
    );
    pendingByContestAndUser = createSimpleLoader(
        async ({ contestId, username }: { contestId: string; username: string }) => {
            // TODO: denormalize DB to make this code simpler and faster
            const submissions = await this.ctx.table(Submission).findAll({ where: { username } });
            const officalEvaluations = await Promise.all(submissions.map(async s => this.getOfficialEvaluation(s)));

            return submissions.filter((s, i) => officalEvaluations[i]?.status === 'PENDING');
        },
    );

    async getContestProblemAssignment(s: Submission): Promise<ContestProblemAssignment> {
        return new ContestProblemAssignment(s.contestId, s.problemName);
    }

    async getSubmissionFiles(s: Submission) {
        return this.ctx.api(SubmissionFileApi).allBySubmissionId.load(s.id);
    }

    /**
     * Extract the files of this submission in the specified base dir.
     * It extract files as: `${base}/${submissionId}/${fieldName}.${fileTypeName}${extension}`
     *
     * @param base base directory
     */
    async extract(s: Submission, base: string) {
        const submissionFiles = await this.getSubmissionFiles(s);
        const submissionPath = path.join(base, s.id);

        for (const submissionFile of submissionFiles) {
            const content = await submissionFile.getContent({ attributes: ['id', 'content'] });
            const { fieldName, fileTypeName } = submissionFile;

            const extension = '.cpp'; // FIXME: determine extension from file type

            const filePath = path.join(submissionPath, `${fieldName}.${fileTypeName}${extension}`);
            await this.ctx.api(FileContentApi).extract(content, filePath);
        }

        return submissionPath;
    }

    async getOfficialEvaluation(s: Submission) {
        return this.ctx.table(Evaluation).findOne({
            where: { submissionId: s.id },
            order: [['createdAt', 'DESC']],
        });
    }

    async getProblem(s: Submission) {
        return new Problem(s.contestId, s.problemName);
    }

    async getMaterial(s: Submission) {
        return this.ctx.api(ProblemMaterialApi).byContestAndProblemName.load({
            contestId: s.contestId,
            problemName: s.problemName,
        });
    }

    async getAwardAchievements(s: Submission) {
        const evaluation = await this.getOfficialEvaluation(s);
        const achievements =
            evaluation !== null ? await this.ctx.api(AchievementApi).allByEvaluationId.load(evaluation.id) : [];
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
                                    ? this.ctx.api(AchievementApi).getScoreGrade(achievement, gradeDomain).score
                                    : null,
                            scoreRange: gradeDomain.scoreRange,
                        };
                    }
                    if (gradeDomain instanceof FulfillmentGradeDomain) {
                        return {
                            __typename: 'FulfillmentField',
                            fulfilled:
                                achievement !== undefined
                                    ? this.ctx.api(AchievementApi).getFulfillmentGrade(achievement).fulfilled
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
        const events =
            evaluation !== null ? await this.ctx.api(EvaluationEventApi).allByEvaluationId.load(evaluation.id) : [];

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
                        __typename: 'HeaderField',
                        index: awardIndex,
                        title: [{ value: `Subtask ${awardIndex}` }],
                    },
                    {
                        __typename: 'HeaderField',
                        index: testCaseIndex,
                        title: [{ value: `Case ${testCaseIndex}` }],
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

        contest: (s, {}, ctx) => ctx.api(ContestApi).fromId(s.contestId),
        user: (s, {}, ctx) =>
            ctx.api(UserApi).validate({
                __typename: 'User',
                contest: ctx.api(ContestApi).fromId(s.contestId),
                username: s.username,
            }),
        problem: (s, {}, ctx) => new Problem(s.contestId, s.problemName),

        participation: ({ username, contestId }, {}, ctx) => new Participation(contestId, username),
        contestProblemAssigment: ({ contestId, problemName }, {}, ctx) =>
            new ContestProblemAssignment(contestId, problemName),

        officialEvaluation: (s, {}, ctx) => ctx.api(SubmissionApi).getOfficialEvaluation(s),
        summaryRow: (s, {}, ctx) => ctx.api(SubmissionApi).getSummaryRow(s),
        feedbackTable: (s, {}, ctx) => ctx.api(SubmissionApi).getFeedbackTable(s),

        createdAt: s => s.createdAt,
        evaluations: (s, {}, ctx) => ctx.api(EvaluationApi).allBySubmissionId.load(s.id),
        files: (s, {}, ctx) => ctx.api(SubmissionApi).getSubmissionFiles(s),
    },
};
