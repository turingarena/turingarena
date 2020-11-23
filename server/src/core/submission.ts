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
import { ScoreField, ScoreGrade, ScoreGradeDomain, ScoreRange } from './feedback/score';
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
    constructor(readonly id: string, readonly ctx: ApiContext) {}
    __typename = 'Submission';

    async contest() {
        return (await this.getTackling()).assignment.problem.contest;
    }

    async user() {
        return (await this.getTackling()).user;
    }

    async problem() {
        return (await this.getTackling()).assignment.problem;
    }

    async participation() {
        const tackling = await this.getTackling();

        return typed<Participation>({
            __typename: 'Participation',
            contest: tackling.assignment.problem.contest,
            user: tackling.user,
        });
    }

    async contestProblemAssigment() {
        return (await this.getTackling()).assignment;
    }

    async officialEvaluation() {
        return this.getOfficialEvaluation();
    }

    async summaryRow() {
        const scoreRange = (await this.getMaterial()).scoreRange;
        const score = (await this.getTotalScore())?.score;

        return {
            __typename: 'Record',
            valence:
                score !== undefined ? (score >= scoreRange.max ? 'SUCCESS' : score > 0 ? 'PARTIAL' : 'FAILURE') : null,
            fields: [
                ...(await this.getAwardAchievements()).map(({ award: { gradeDomain }, achievement }) => {
                    if (gradeDomain instanceof ScoreGradeDomain) {
                        return new ScoreField(
                            gradeDomain.scoreRange,
                            achievement !== undefined ? achievement.getScoreGrade(gradeDomain).score : null,
                        );
                    }
                    if (gradeDomain instanceof FulfillmentGradeDomain) {
                        return {
                            __typename: 'FulfillmentField',
                            fulfilled: achievement !== undefined ? achievement.getFulfillmentGrade().fulfilled : null,
                        };
                    }
                    throw new Error(`unexpected grade domain ${gradeDomain}`);
                }),
                new ScoreField(scoreRange, score !== undefined ? score : null),
            ],
        };
    }

    async feedbackTable() {
        return this.getFeedbackTable();
    }

    async createdAt() {
        return (await this.ctx.api(SubmissionCache).dataLoader.load(this.id)).createdAt;
    }

    async evaluations() {
        return this.ctx.api(EvaluationCache).allBySubmissionId.load(this.id);
    }

    async files() {
        return this.getSubmissionFiles();
    }

    static fromId(id: string, ctx: ApiContext): Submission {
        return new Submission(id, ctx);
    }

    async validate() {
        await this.ctx.api(SubmissionCache).dataLoader.load(this.id);

        return this;
    }

    async getSubmissionFiles() {
        return this.ctx.api(SubmissionFileCache).allBySubmissionId.load(this.id);
    }

    async getTackling() {
        const { contestId, problemName, username } = await this.ctx.api(SubmissionCache).dataLoader.load(this.id);

        const contest = new Contest(contestId, this.ctx);

        return new ContestProblemAssignmentUserTackling(
            new ContestProblemAssignment(new Problem(contest, problemName, this.ctx)),
            new User(contest, username),
            this.ctx,
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
        const submissionPath = path.join(base, this.id);

        for (const submissionFile of submissionFiles) {
            const content = await submissionFile.getContent({ attributes: ['id', 'content'] });
            const { fieldName, fileTypeName } = submissionFile;

            const extension = fileTypeName;

            const filePath = path.join(submissionPath, `${fieldName}.${fileTypeName}.${extension}`);
            await this.ctx.api(FileContentApi).extract(content, filePath);
        }

        return submissionPath;
    }

    async getOfficialEvaluation() {
        return this.ctx.table(Evaluation).findOne({
            where: { submissionId: this.id },
            order: [['createdAt', 'DESC']],
        });
    }

    async getMaterial() {
        const { assignment } = await this.getTackling();

        return this.ctx.api(ProblemMaterialApi).dataLoader.load(assignment.problem.id());
    }

    async getAwardAchievements() {
        const evaluation = await this.getOfficialEvaluation();
        const achievements =
            evaluation !== null ? await this.ctx.api(AchievementCache).allByEvaluationId.load(evaluation.id) : [];
        const material = await this.getMaterial();

        return material.awards.map((award, awardIndex) => ({
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

    async getFeedbackTable() {
        const {
            awards,
            taskInfo,
            evaluationFeedbackColumns,
            timeLimitSeconds,
            memoryLimitBytes,
        } = await this.getMaterial();
        const { scoring } = taskInfo.IOI;

        const limitsMarginMultiplier = 2;
        const memoryUnitBytes = 1024;
        const warningWatermarkMultiplier = 0.2;

        const evaluation = await this.getOfficialEvaluation();
        const events =
            evaluation !== null ? await this.ctx.api(EvaluationEventCache).allByEvaluationId.load(evaluation.id) : [];

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
                    new ScoreField(new ScoreRange(1, 2, true), score),
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
    dataLoader = createSimpleLoader((id: string) => this.ctx.table(SubmissionData).findByPk(id));

    allByTackling = createSimpleLoader(async (id: string) => {
        const cpaut = ContestProblemAssignmentUserTackling.fromId(id, this.ctx);
        const problemName = cpaut.assignment.problem.name;
        const contestId = cpaut.assignment.contest().id;
        const username = cpaut.user.username;

        return (
            await this.ctx
                .table(SubmissionData)
                .findAll({ where: { problemName, contestId, username }, order: [['createdAt', 'DESC']] })
        ).map(data => Submission.fromId(data.id, this.ctx));
    });

    pendingByContestAndUser = createSimpleLoader(
        async ({ contestId, username }: { contestId: string; username: string }) => {
            // TODO: denormalize DB to make this code simpler and faster
            const submissions = await this.ctx.table(SubmissionData).findAll({ where: { username } });
            const officialEvaluations = await Promise.all(
                submissions.map(async s => Submission.fromId(s.id, this.ctx).getOfficialEvaluation()),
            );

            return submissions
                .filter((s, i) => officialEvaluations[i]?.status === 'PENDING')
                .map(s => Submission.fromId(s.id, this.ctx));
        },
    );
}
