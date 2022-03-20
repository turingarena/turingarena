import { gql } from 'apollo-server-core';
import * as path from 'path';
import { AllowNull, Column, Table } from 'sequelize-typescript';
import { ApiCache } from '../main/api-cache';
import { ApiContext } from '../main/api-context';
import { createSimpleLoader, UuidBaseModel } from '../main/base-model';
import { ApiInputValue, ApiOutputValue } from '../main/graphql-types';
import { unreachable } from '../util/unreachable';
import { Contest } from './contest';
import { ApiDateTime } from './data/date-time';
import { ApiTable, Record } from './data/field';
import { FulfillmentField, FulfillmentGradeDomain } from './data/fulfillment';
import { ScoreField, ScoreGradeDomain } from './data/score';
import { LiveEvaluationService } from './evaluate';
import { Evaluation, EvaluationCache } from './evaluation';
import { TestCaseData } from './evaluation-outcome';
import { extractFile } from './files/file-content';
import { ObjectiveDefinition } from './objective-definition';
import { ProblemDefinition } from './problem-definition';
import { ProblemMaterialCache } from './problem-definition-material';
import { ProblemInstance } from './problem-instance';
import { ProblemUndertaking } from './problem-undertaking';
import { SubmissionItemCache } from './submission-item';

export const submissionSchema = gql`
    type Submission {
        id: ID!

        problem: ProblemInstance!
        user: User!

        items: [SubmissionItem!]!
        createdAt: DateTime!
        officialEvaluation: Evaluation
        evaluations: [Evaluation!]!

        summaryRow: Record!
        feedbackTable: Table!

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

    async user() {
        return (await this.getUndertaking()).user;
    }

    async problem() {
        return (await this.getUndertaking()).instance;
    }

    async officialEvaluation() {
        const data = await this.ctx.cache(EvaluationCache).officialBySubmission.load(this.id);
        if (data === null) return null;

        return new Evaluation(data.id, this.ctx);
    }

    async getOutcome(objective: ObjectiveDefinition) {
        const evaluation = await this.officialEvaluation();
        return evaluation?.getOutcome(objective) ?? null;
    }

    async summaryRow() {
        const scoreRange = (await this.getProblemMaterial()).scoreRange;
        const score = (await this.getTotalScore())?.score;
        const outcomes = await this.getObjectiveOutcomes();
        const material = await this.getProblemMaterial();

        const objectiveFields = material.objectives.map(objective => {
            const { gradeDomain } = objective;
            if (gradeDomain instanceof ScoreGradeDomain) {
                return new ScoreField(
                    gradeDomain.scoreRange,
                    outcomes !== null ? outcomes.get(objective)?.getScoreGrade(gradeDomain).score ?? 0 : null,
                );
            }
            if (gradeDomain instanceof FulfillmentGradeDomain) {
                return new FulfillmentField(
                    outcomes !== null ? outcomes.get(objective)?.getFulfillmentGrade().fulfilled ?? false : null,
                );
            }
            throw unreachable();
        });

        const totalScoreField = new ScoreField(scoreRange, score !== undefined ? score : null);
        const valence =
            score !== undefined ? (score >= scoreRange.max ? 'SUCCESS' : score > 0 ? 'PARTIAL' : 'FAILURE') : null;

        return new Record([...objectiveFields, totalScoreField], valence);
    }

    async feedbackTable() {
        const problemMaterial = await this.getProblemMaterial();
        const { objectives, taskInfo, evaluationFeedbackTableDefinition } = problemMaterial;
        const { scoring } = taskInfo.IOI;

        const events = await this.getLiveEvaluationEvents();

        const testCasesData = objectives
            .flatMap((objective, objectiveIndex) =>
                Array.from(
                    { length: scoring.subtasks[objectiveIndex].testcases },
                    (unused, i): Omit<TestCaseData, 'testCaseIndex'> => ({
                        objective,
                        objectiveIndex,
                        timeUsage: null,
                        memoryUsage: null,
                        message: null,
                        score: null,
                    }),
                ),
            )
            .map((data, i): TestCaseData => ({ ...data, testCaseIndex: i }));

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

        return ApiTable.fromColumnDefinitions(evaluationFeedbackTableDefinition, testCasesData, ({ score }) =>
            score !== null ? (score >= 1 ? 'SUCCESS' : score > 0 ? 'PARTIAL' : 'FAILURE') : null,
        );
    }

    private async getLiveEvaluationEvents() {
        const liveEvaluation = this.ctx.service(LiveEvaluationService).getBySubmission(this.id);
        if (liveEvaluation !== null) return liveEvaluation.events;

        const evaluation = await this.officialEvaluation();

        return evaluation?.events() ?? [];
    }

    async createdAt() {
        return ApiDateTime.fromJSDate((await this.ctx.cache(SubmissionCache).byId.load(this.id)).createdAt);
    }

    async evaluations() {
        return (await this.ctx.cache(EvaluationCache).bySubmission.load(this.id)).map(
            ({ id }) => new Evaluation(id, this.ctx),
        );
    }

    async items() {
        return this.ctx.cache(SubmissionItemCache).bySubmission.load(this.id);
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

    async getUndertaking() {
        const { contestId, problemName, username } = await this.ctx.cache(SubmissionCache).byId.load(this.id);

        const contest = new Contest(contestId, this.ctx);

        return new ProblemUndertaking(
            new ProblemInstance(new ProblemDefinition(contest, problemName)),
            await contest.getUserByName(username),
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
        const items = await this.items();
        const submissionPath = path.join(base, this.id);

        for (const item of items) {
            const filePath = path.join(submissionPath, item.file.name);
            await extractFile(item.file.content, filePath);
        }

        return submissionPath;
    }

    async getProblemMaterial() {
        const { instance } = await this.getUndertaking();

        return this.ctx.cache(ProblemMaterialCache).byId.load(instance.definition.id());
    }

    async getObjectiveOutcomes() {
        return (await this.officialEvaluation())?.getObjectiveOutcomes() ?? null;
    }

    async getTotalScore() {
        const evaluation = await this.officialEvaluation();
        if (!evaluation) return null;
        return evaluation.getTotalScore();
    }

    async getTotalScoreField() {
        return new ScoreField(
            (await this.getProblemMaterial()).scoreRange,
            (await this.getTotalScore())?.score ?? null,
        );
    }
}

export type SubmissionInput = ApiInputValue<'SubmissionInput'>;

export class SubmissionCache extends ApiCache {
    byId = createSimpleLoader((id: string) => this.ctx.table(SubmissionData).findByPk(id));

    byUndertaking = createSimpleLoader(async (id: string) => {
        const cpaut = await ProblemUndertaking.fromId(id, this.ctx);
        const problemName = cpaut.instance.definition.baseName;
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
            const submissions = await this.ctx.table(SubmissionData).findAll({ where: { contestId, username } });

            return submissions
                .filter((s, i) => this.ctx.service(LiveEvaluationService).getBySubmission(s.id))
                .map(s => Submission.fromId(s.id, this.ctx));
        },
    );

    byContest = createSimpleLoader(async (contestId: string) => {
        const submissions = await this.ctx.table(SubmissionData).findAll({ where: { contestId } });
        return submissions.map(s => Submission.fromId(s.id, this.ctx));
    });
}
