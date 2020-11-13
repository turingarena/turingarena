import { gql } from 'apollo-server-core';
import * as path from 'path';
import { AllowNull, Column, ForeignKey, Table } from 'sequelize-typescript';
import { __generated_SubmissionInput } from '../generated/graphql-types';
import { ApiObject } from '../main/api';
import { ApiContext } from '../main/api-context';
import { createSimpleLoader, UuidBaseModel } from '../main/base-model';
import { typed } from '../util/types';
import { AchievementApi } from './achievement';
import { ContestApi, ContestData } from './contest';
import { ContestProblemAssignment } from './contest-problem-assignment';
import { ContestProblemAssignmentUserTackling } from './contest-problem-assignment-user-tackling';
import { Evaluation, EvaluationApi, EvaluationStatus } from './evaluation';
import { EvaluationEventApi } from './evaluation-event';
import { FulfillmentGradeDomain } from './feedback/fulfillment';
import { ScoreGrade, ScoreGradeDomain } from './feedback/score';
import { FileContentApi } from './files/file-content';
import { ProblemMaterialApi } from './material/problem-material';
import { Participation } from './participation';
import { Problem } from './problem';
import { SubmissionFileApi } from './submission-file';
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
        return (await ctx.api(SubmissionApi).getTackling(this)).assignment.problem.contest;
    }
    async user({}, ctx: ApiContext) {
        return (await ctx.api(SubmissionApi).getTackling(this)).user;
    }
    async problem({}, ctx: ApiContext) {
        return (await ctx.api(SubmissionApi).getTackling(this)).assignment.problem;
    }
    async participation({}, ctx: ApiContext) {
        const tackling = await ctx.api(SubmissionApi).getTackling(this);

        return typed<Participation>({
            __typename: 'Participation',
            contest: tackling.assignment.problem.contest,
            user: tackling.user,
        });
    }
    async contestProblemAssigment({}, ctx: ApiContext) {
        return (await ctx.api(SubmissionApi).getTackling(this)).assignment;
    }
    officialEvaluation({}, ctx: ApiContext) {
        return ctx.api(SubmissionApi).getOfficialEvaluation(this);
    }
    summaryRow({}, ctx: ApiContext) {
        return ctx.api(SubmissionApi).getSummaryRow(this);
    }
    feedbackTable({}, ctx: ApiContext) {
        return ctx.api(SubmissionApi).getFeedbackTable(this);
    }
    async createdAt({}, ctx: ApiContext) {
        return (await ctx.api(SubmissionApi).dataLoader.load(this)).createdAt;
    }
    evaluations({}, ctx: ApiContext) {
        return ctx.api(EvaluationApi).allBySubmissionId.load(this.id);
    }
    files({}, ctx: ApiContext) {
        return ctx.api(SubmissionApi).getSubmissionFiles(this);
    }
}

export interface SubmissionModelRecord {
    Submission: Submission;
}

export type SubmissionInput = __generated_SubmissionInput;

export class SubmissionApi extends ApiObject {
    fromId(id: string) {
        return new Submission(id);
    }

    dataLoader = createSimpleLoader((s: Submission) => this.ctx.table(SubmissionData).findByPk(s.id));

    async validate(submission: Submission) {
        await this.dataLoader.load(submission);

        return submission;
    }

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
            ).map(data => this.fromId(data.id)),
    );

    pendingByContestAndUser = createSimpleLoader(
        async ({ contestId, username }: { contestId: string; username: string }) => {
            // TODO: denormalize DB to make this code simpler and faster
            const submissions = await this.ctx.table(SubmissionData).findAll({ where: { username } });
            const officalEvaluations = await Promise.all(
                submissions.map(async s => this.getOfficialEvaluation(this.fromId(s.id))),
            );

            return submissions
                .filter((s, i) => officalEvaluations[i]?.status === 'PENDING')
                .map(s => this.fromId(s.id));
        },
    );

    async getSubmissionFiles(s: Submission) {
        return this.ctx.api(SubmissionFileApi).allBySubmissionId.load(s.id);
    }

    async getTackling(s: Submission) {
        const { contestId, problemName, username } = await this.dataLoader.load(s);

        const contest = this.ctx.api(ContestApi).fromId(contestId);

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
    async extract(s: Submission, base: string) {
        const submissionFiles = await this.getSubmissionFiles(s);
        const submissionPath = path.join(base, s.id);

        for (const submissionFile of submissionFiles) {
            const content = await submissionFile.getContent({ attributes: ['id', 'content'] });
            const { fieldName, fileTypeName } = submissionFile;

            const extension = fileTypeName;

            const filePath = path.join(submissionPath, `${fieldName}.${fileTypeName}.${extension}`);
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

    async getMaterial(s: Submission) {
        const { assignment } = await this.getTackling(s);

        return this.ctx.api(ProblemMaterialApi).dataLoader.load(assignment.problem);
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
                    return [achievement.getScoreGrade(gradeDomain)];
                }

                return [];
            }),
        );
    }

    async getSummaryRow(s: Submission) {
        const scoreRange = (await this.getMaterial(s)).scoreRange;
        const score = (await this.getTotalScore(s))?.score;

        return {
            __typename: 'Record',
            valence:
                score !== undefined ? (score >= scoreRange.max ? 'SUCCESS' : score > 0 ? 'PARTIAL' : 'FAILURE') : null,
            fields: [
                ...(await this.getAwardAchievements(s)).map(({ award: { gradeDomain }, achievement }) => {
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
                            fulfilled: achievement !== undefined ? achievement.getFulfillmentGrade.fulfilled : null,
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

    async getFeedbackTable(s: Submission) {
        const {
            awards,
            taskInfo,
            evaluationFeedbackColumns,
            timeLimitSeconds,
            memoryLimitBytes,
        } = await this.getMaterial(s);
        const { scoring } = taskInfo.IOI;

        const limitsMarginMultiplier = 2;
        const memoryUnitBytes = 1024;
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
