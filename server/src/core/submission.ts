import { gql } from 'apollo-server-core';
import * as path from 'path';
import { AllowNull, Column, ForeignKey, Table } from 'sequelize-typescript';
import { __generated_SubmissionInput } from '../generated/graphql-types';
import { ApiObject } from '../main/api';
import { ApiContext } from '../main/api-context';
import { createSimpleLoader, UuidBaseModel } from '../main/base-model';
import { typed } from '../util/types';
import { AchievementCache } from './achievement';
import { Contest, ContestData } from './contest';
import { ContestProblemAssignment } from './contest-problem-assignment';
import { ContestProblemAssignmentUserTackling } from './contest-problem-assignment-user-tackling';
import { Evaluation, EvaluationCache, EvaluationStatus } from './evaluation';
import { EvaluationEventCache } from './evaluation-event';
import { FulfillmentGradeDomain } from './feedback/fulfillment';
import { ScoreGrade, ScoreGradeDomain } from './feedback/score';
import { FileContentApi } from './files/file-content';
import { ProblemMaterialApi } from './material/problem-material';
import { Participation } from './participation';
import { Problem } from './problem';
import { SubmissionFileCache } from './submission-file';
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

@Table({ updatedAt: false, tableName: 'submissions' })
export class SubmissionData extends UuidBaseModel<SubmissionData> {
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

export class Submission {
    constructor(readonly id: string) {}
    __typename = 'Submission';

    async contest({}, ctx: ApiContext) {
        return (await this.getTackling(ctx)).assignment.problem.contest;
    }

    async user({}, ctx: ApiContext) {
        return (await this.getTackling(ctx)).user;
    }

    async problem({}, ctx: ApiContext) {
        return (await this.getTackling(ctx)).assignment.problem;
    }

    async participation({}, ctx: ApiContext) {
        const tackling = await this.getTackling(ctx);

        return typed<Participation>({
            __typename: 'Participation',
            contest: tackling.assignment.problem.contest,
            user: tackling.user,
        });
    }

    async contestProblemAssigment({}, ctx: ApiContext) {
        return (await this.getTackling(ctx)).assignment;
    }

    officialEvaluation({}, ctx: ApiContext) {
        return this.getOfficialEvaluation(ctx);
    }

    async summaryRow({}, ctx: ApiContext) {
        const scoreRange = (await this.getMaterial(ctx)).scoreRange;
        const score = (await this.getTotalScore(ctx))?.score;

        return {
            __typename: 'Record',
            valence:
                score !== undefined ? (score >= scoreRange.max ? 'SUCCESS' : score > 0 ? 'PARTIAL' : 'FAILURE') : null,
            fields: [
                ...(await this.getAwardAchievements(ctx)).map(({ award: { gradeDomain }, achievement }) => {
                    if (gradeDomain instanceof ScoreGradeDomain) {
                        return {
                            __typename: 'ScoreField',
                            score: achievement !== undefined ? achievement.getScoreGrade(gradeDomain).score : null,
                            scoreRange: gradeDomain.scoreRange,
                        };
                    }
                    if (gradeDomain instanceof FulfillmentGradeDomain) {
                        return {
                            __typename: 'FulfillmentField',
                            fulfilled: achievement !== undefined ? achievement.getFulfillmentGrade().fulfilled : null,
                        };
                    }
                    throw new Error(`unexpected grade domain ${gradeDomain}`);
                }),
                {
                    __typename: 'ScoreField',
                    score,
                    scoreRange,
                },
            ],
        };
    }

    feedbackTable({}, ctx: ApiContext) {
        return this.getFeedbackTable(ctx);
    }

    async createdAt({}, ctx: ApiContext) {
        return (await ctx.api(SubmissionCache).dataLoader.load(this)).createdAt;
    }

    evaluations({}, ctx: ApiContext) {
        return ctx.api(EvaluationCache).allBySubmissionId.load(this.id);
    }

    files({}, ctx: ApiContext) {
        return this.getSubmissionFiles(ctx);
    }

    static fromId(id: string): Submission {
        return new Submission(id);
    }

    async validate(ctx: ApiContext) {
        await ctx.api(SubmissionCache).dataLoader.load(this);

        return this;
    }

    async getSubmissionFiles(ctx: ApiContext) {
        return ctx.api(SubmissionFileCache).allBySubmissionId.load(this.id);
    }

    async getTackling(ctx: ApiContext) {
        const { contestId, problemName, username } = await ctx.api(SubmissionCache).dataLoader.load(this);

        const contest = new Contest(contestId);

        return new ContestProblemAssignmentUserTackling(
            new ContestProblemAssignment(new Problem(contest, problemName)),
            new User(contest, username),
        );
    }

    /**
     * Extract the files of this submission in the specified base dir.
     * It extract files as: `${base}/${submissionId}/${fieldName}.${fileTypeName}${extension}`
     *
     * @param base base directory
     */
    async extract(base: string, ctx: ApiContext) {
        const submissionFiles = await this.getSubmissionFiles(ctx);
        const submissionPath = path.join(base, this.id);

        for (const submissionFile of submissionFiles) {
            const content = await submissionFile.getContent({ attributes: ['id', 'content'] });
            const { fieldName, fileTypeName } = submissionFile;

            const extension = fileTypeName;

            const filePath = path.join(submissionPath, `${fieldName}.${fileTypeName}.${extension}`);
            await ctx.api(FileContentApi).extract(content, filePath);
        }

        return submissionPath;
    }

    async getOfficialEvaluation(ctx: ApiContext) {
        return ctx.table(Evaluation).findOne({
            where: { submissionId: this.id },
            order: [['createdAt', 'DESC']],
        });
    }

    async getMaterial(ctx: ApiContext) {
        const { assignment } = await this.getTackling(ctx);

        return ctx.api(ProblemMaterialApi).dataLoader.load(assignment.problem);
    }

    async getAwardAchievements(ctx: ApiContext) {
        const evaluation = await this.getOfficialEvaluation(ctx);
        const achievements =
            evaluation !== null ? await ctx.api(AchievementCache).allByEvaluationId.load(evaluation.id) : [];
        const material = await this.getMaterial(ctx);

        return material.awards.map((award, awardIndex) => ({
            award,
            achievement: achievements.find(a => a.awardIndex === awardIndex),
        }));
    }

    async getTotalScore(ctx: ApiContext) {
        if ((await this.getOfficialEvaluation(ctx))?.status !== EvaluationStatus.SUCCESS) return undefined;

        return ScoreGrade.total(
            (await this.getAwardAchievements(ctx)).flatMap(({ achievement, award: { gradeDomain } }) => {
                if (gradeDomain instanceof ScoreGradeDomain && achievement !== undefined) {
                    return [achievement.getScoreGrade(gradeDomain)];
                }

                return [];
            }),
        );
    }

    async getFeedbackTable(ctx: ApiContext) {
        const {
            awards,
            taskInfo,
            evaluationFeedbackColumns,
            timeLimitSeconds,
            memoryLimitBytes,
        } = await this.getMaterial(ctx);
        const { scoring } = taskInfo.IOI;

        const limitsMarginMultiplier = 2;
        const memoryUnitBytes = 1024;
        const warningWatermarkMultiplier = 0.2;

        const evaluation = await this.getOfficialEvaluation(ctx);
        const events =
            evaluation !== null ? await ctx.api(EvaluationEventCache).allByEvaluationId.load(evaluation.id) : [];

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
            if (typeof data === 'object' && 'IOITestcaseScore' in data) {
                const { testcase, score, message } = data.IOITestcaseScore;
                const testCaseData = testCasesData[testcase];
                testCaseData.message = message;
                testCaseData.score = score;
            }

            if (typeof data === 'object' && 'IOIEvaluation' in data) {
                const { status, testcase } = data.IOIEvaluation;
                if (typeof status === 'object' && 'Done' in status) {
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
                valence: score !== null ? (score >= 1 ? 'SUCCESS' : score > 0 ? 'PARTIAL' : 'FAILURE') : null,
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
                        timeUsageMaxRelevant: { seconds: timeLimitSeconds * limitsMarginMultiplier },
                        timeUsagePrimaryWatermark: { seconds: timeLimitSeconds },
                        valence:
                            timeUsage === null
                                ? null
                                : timeUsage <= warningWatermarkMultiplier * timeLimitSeconds
                                ? 'NOMINAL'
                                : timeUsage <= timeLimitSeconds
                                ? 'WARNING'
                                : 'FAILURE',
                    },
                    {
                        __typename: 'MemoryUsageField',
                        memoryUsage: memoryUsage !== null ? { bytes: memoryUsage * memoryUnitBytes } : null,
                        memoryUsageMaxRelevant: {
                            bytes: memoryLimitBytes * limitsMarginMultiplier,
                        },
                        memoryUsagePrimaryWatermark: {
                            bytes: memoryLimitBytes,
                        },
                        valence:
                            memoryUsage === null
                                ? null
                                : memoryUsage * memoryUnitBytes <= warningWatermarkMultiplier * memoryLimitBytes
                                ? 'NOMINAL'
                                : memoryUsage * memoryUnitBytes <= memoryLimitBytes
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

export interface SubmissionModelRecord {
    Submission: Submission;
}

export type SubmissionInput = __generated_SubmissionInput;

export class SubmissionCache extends ApiObject {
    dataLoader = createSimpleLoader((s: Submission) => this.ctx.table(SubmissionData).findByPk(s.id));

    allByTackling = createSimpleLoader(
        async ({
            assignment: {
                problem: {
                    contest: { id: contestId },
                    name: problemName,
                },
            },
            user: { username },
        }: ContestProblemAssignmentUserTackling) =>
            (
                await this.ctx
                    .table(SubmissionData)
                    .findAll({ where: { problemName, contestId, username }, order: [['createdAt', 'DESC']] })
            ).map(data => Submission.fromId(data.id)),
    );

    pendingByContestAndUser = createSimpleLoader(
        async ({ contestId, username }: { contestId: string; username: string }) => {
            // TODO: denormalize DB to make this code simpler and faster
            const submissions = await this.ctx.table(SubmissionData).findAll({ where: { username } });
            const officalEvaluations = await Promise.all(
                submissions.map(async s => Submission.fromId(s.id).getOfficialEvaluation(this.ctx)),
            );

            return submissions
                .filter((s, i) => officalEvaluations[i]?.status === 'PENDING')
                .map(s => Submission.fromId(s.id));
        },
    );
}
