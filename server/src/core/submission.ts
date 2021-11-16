import { UIMessage } from '@edomora97/task-maker';
import { gql } from 'apollo-server-core';
import * as path from 'path';
import { AllowNull, Column, ForeignKey, Table } from 'sequelize-typescript';
import { ApiCache } from '../main/api-cache';
import { ApiContext } from '../main/api-context';
import { createSimpleLoader, UuidBaseModel } from '../main/base-model';
import { ApiInputValue, ApiOutputValue } from '../main/graphql-types';
import { typed } from '../util/types';
import { unreachable } from '../util/unreachable';
import { OutcomeCache } from './achievement';
import { Contest, ContestData } from './contest';
import { ProblemInstance } from './problem-instance';
import { ProblemTackling } from './problem-tackling';
import { LiveEvaluationService } from './evaluate';
import { Evaluation, EvaluationCache } from './evaluation';
import { FulfillmentField, FulfillmentGradeDomain } from './feedback/fulfillment';
import { ScoreField, ScoreGrade, ScoreGradeDomain, ScoreRange } from './feedback/score';
import { extractFile } from './files/file-content';
import { ProblemMaterialCache } from './problem-definition-material';
import { Text } from './text';
import { Participation } from './participation';
import { ProblemDefinition } from './problem-definition';
import { SubmissionFileCache } from './submission-file';
import { User } from './user';
import { ApiDateTime } from './util/date-time';

export const submissionSchema = gql`
    type Submission {
        id: ID!

        problem: ProblemDefinition!
        user: User!
        contest: Contest!

        contestProblemAssigment: ProblemInstance!
        participation: Participation!

        files: [SubmissionFile!]!
        createdAt: DateTime!
        officialEvaluation: Evaluation
        evaluations: [Evaluation!]!

        summaryRow: Record!
        feedbackTable: FeedbackTable!

        totalScore: ScoreGrade
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

export class Submission implements ApiOutputValue<'Submission'> {
    constructor(readonly id: string, readonly ctx: ApiContext) {}
    __typename = 'Submission' as const;

    async contest() {
        return (await this.getTackling()).instance.definition.contest;
    }

    async user() {
        return (await this.getTackling()).user;
    }

    async problem() {
        return (await this.getTackling()).instance.definition;
    }

    async participation() {
        const tackling = await this.getTackling();

        return typed<Participation>({
            __typename: 'Participation',
            contest: tackling.instance.definition.contest,
            user: tackling.user,
        });
    }

    async contestProblemAssigment() {
        return (await this.getTackling()).instance;
    }

    async officialEvaluation() {
        const data = await this.getOfficialEvaluationData();
        if (data === null) return null;

        return new Evaluation(data.id, this.ctx);
    }

    async summaryRow(): Promise<ApiOutputValue<'Record'>> {
        const scoreRange = (await this.getMaterial()).scoreRange;
        const score = (await this.getTotalScore())?.score;
        const outcomes = await this.getObjectiveOutcomes();
        const material = await this.getMaterial();

        return {
            __typename: 'Record',
            valence:
                score !== undefined ? (score >= scoreRange.max ? 'SUCCESS' : score > 0 ? 'PARTIAL' : 'FAILURE') : null,
            fields: [
                ...material.objectives.map(objective => {
                    const { gradeDomain } = objective;
                    if (gradeDomain instanceof ScoreGradeDomain) {
                        return new ScoreField(
                            gradeDomain.scoreRange,
                            outcomes !== null
                                ? outcomes.get(objective)?.getScoreGrade(gradeDomain).score ?? 0
                                : null,
                        );
                    }
                    if (gradeDomain instanceof FulfillmentGradeDomain) {
                        return new FulfillmentField(
                            outcomes !== null
                                ? outcomes.get(objective)?.getFulfillmentGrade().fulfilled ?? false
                                : null,
                        );
                    }
                    throw unreachable();
                }),
                new ScoreField(scoreRange, score !== undefined ? score : null),
            ],
        };
    }

    async feedbackTable(): Promise<ApiOutputValue<'FeedbackTable'>> {
        const {
            objectives,
            taskInfo,
            evaluationFeedbackColumns,
            timeLimitSeconds,
            memoryLimitBytes,
        } = await this.getMaterial();
        const { scoring } = taskInfo.IOI;

        const limitsMarginMultiplier = 2;
        const memoryUnitBytes = 1024;
        const warningWatermarkMultiplier = 0.2;

        const events = await this.getLiveEvaluationEvents();

        const testCasesData = objectives.flatMap((objective, objectiveIndex) =>
            new Array(scoring.subtasks[objectiveIndex].testcases).fill(0).map(() => ({
                objective,
                objectiveIndex,
                timeUsage: null as number | null,
                memoryUsage: null as number | null,
                message: null as string | null,
                score: null as number | null,
            })),
        );

        let compilationError: string | null = null;

        for (const event of events ?? []) {
            if (
                typeof event === 'object' &&
                'Compilation' in event &&
                typeof event.Compilation.status === 'object' &&
                'Done' in event.Compilation.status &&
                !(
                    typeof event.Compilation.status.Done.result.status === 'object' &&
                    'ReturnCode' in event.Compilation.status.Done.result.status &&
                    event.Compilation.status.Done.result.status.ReturnCode === 0
                )
            ) {
                compilationError = (event.Compilation.status.Done.result.stderr ?? [])
                    .map(x => String.fromCharCode(x))
                    .join();
            }

            if (typeof event === 'object' && 'IOITestcaseScore' in event) {
                const { testcase, score, message } = event.IOITestcaseScore;
                const testCaseData = testCasesData[testcase];
                testCaseData.message = message;
                testCaseData.score = score;
            }

            if (typeof event === 'object' && 'IOIEvaluation' in event) {
                const { status, testcase } = event.IOIEvaluation;
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
            rows: testCasesData.map(
                ({ objectiveIndex, score, message, timeUsage, memoryUsage }, testCaseIndex): ApiOutputValue<'Record'> => ({
                    valence: score !== null ? (score >= 1 ? 'SUCCESS' : score > 0 ? 'PARTIAL' : 'FAILURE') : null,
                    fields: [
                        {
                            __typename: 'HeaderField',
                            index: objectiveIndex,
                            title: new Text([{ value: `Subtask ${objectiveIndex}` }]),
                        },
                        {
                            __typename: 'HeaderField',
                            index: testCaseIndex,
                            title: new Text([{ value: `Case ${testCaseIndex}` }]),
                        },
                        {
                            __typename: 'TimeUsageField',
                            timeUsage: timeUsage !== null ? { seconds: timeUsage } : null,
                            timeUsageMaxRelevant: { seconds: timeLimitSeconds * limitsMarginMultiplier },
                            timeUsageWatermark: { seconds: timeLimitSeconds },
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
                            memoryUsageWatermark: {
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
                            message: new Text([{ value: `${message ?? ``}` }]),
                            valence: null,
                        },
                        new ScoreField(new ScoreRange(1, 2, true), score),
                    ],
                }),
            ),
        };
    }

    private async getLiveEvaluationEvents() {
        const liveEvaluation = this.ctx.service(LiveEvaluationService).getBySubmission(this.id);
        if (liveEvaluation !== null) return liveEvaluation.events;

        const evaluation = await this.getOfficialEvaluationData();
        if (evaluation !== null) return JSON.parse(evaluation.eventsJson) as UIMessage[];

        return [];
    }

    async createdAt() {
        return ApiDateTime.fromJSDate((await this.ctx.cache(SubmissionCache).byId.load(this.id)).createdAt);
    }

    async evaluations() {
        return (await this.ctx.cache(EvaluationCache).bySubmission.load(this.id)).map(
            ({ id }) => new Evaluation(id, this.ctx),
        );
    }

    async files() {
        return this.getSubmissionFiles();
    }

    async totalScore() {
        return this.getTotalScore();
    }

    static fromId(id: string, ctx: ApiContext): Submission {
        return new Submission(id, ctx);
    }

    async validate() {
        await this.ctx.cache(SubmissionCache).byId.load(this.id);

        return this;
    }

    async getSubmissionFiles() {
        return this.ctx.cache(SubmissionFileCache).bySubmission.load(this.id);
    }

    async getTackling() {
        const { contestId, problemName, username } = await this.ctx.cache(SubmissionCache).byId.load(this.id);

        const contest = new Contest(contestId, this.ctx);

        return new ProblemTackling(
            new ProblemInstance(new ProblemDefinition(contest, problemName, this.ctx)),
            new User(contest, username, this.ctx),
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
            await extractFile(content, filePath);
        }

        return submissionPath;
    }

    async getOfficialEvaluationData() {
        return this.ctx.cache(EvaluationCache).officialBySubmission.load(this.id);
    }

    async getMaterial() {
        const { instance } = await this.getTackling();

        return this.ctx.cache(ProblemMaterialCache).byId.load(instance.definition.id());
    }

    async getObjectiveOutcomes() {
        const evaluation = await this.getOfficialEvaluationData();
        if (evaluation === null) return null;

        const outcomes = await this.ctx.cache(OutcomeCache).byEvaluation.load(evaluation.id);
        const material = await this.getMaterial();

        return new Map(
            material.objectives.map((objective, objectiveIndex) => [
                objective,
                outcomes.find(a => a.objectiveIndex === objectiveIndex) ?? null,
            ]),
        );
    }

    async getTotalScore() {
        const outcomes = await this.getObjectiveOutcomes();
        if (!outcomes) return null;
        const material = await this.getMaterial();

        return ScoreGrade.total(
            material.objectives
                .map(objective => {
                    if (objective.gradeDomain instanceof ScoreGradeDomain) {
                        return outcomes.get(objective)?.getScoreGrade(objective.gradeDomain) ?? null;
                    }

                    return null;
                })
                .flatMap(x => (x === null ? [] : [x])),
        );
    }
}

export type SubmissionInput = ApiInputValue<'SubmissionInput'>;

export class SubmissionCache extends ApiCache {
    byId = createSimpleLoader((id: string) => this.ctx.table(SubmissionData).findByPk(id));

    byTackling = createSimpleLoader(async (id: string) => {
        const cpaut = ProblemTackling.fromId(id, this.ctx);
        const problemName = cpaut.instance.definition.name;
        const contestId = cpaut.instance.contest().id;
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

            return submissions
                .filter((s, i) => this.ctx.service(LiveEvaluationService).getBySubmission(s.id))
                .map(s => Submission.fromId(s.id, this.ctx));
        },
    );
}
