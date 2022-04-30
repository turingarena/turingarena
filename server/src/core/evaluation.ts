import { UIMessage } from '@edomora97/task-maker';
import { gql } from 'apollo-server-core';
import { AllowNull, Column, ForeignKey, Index, Table } from 'sequelize-typescript';
import { ApiCache } from '../main/api-cache';
import { ApiContext } from '../main/api-context';
import { createByIdDataLoader, createSimpleLoader, UuidBaseModel } from '../main/base-model';
import { ApiOutputValue } from '../main/graphql-types';
import { ScoreGrade, ScoreGradeDomain } from './data/score';
import { ObjectiveDefinition } from './objective-definition';
import { OutcomeCache, OutcomeData } from './outcome';
import { ProblemMaterial } from './problem-definition-material';
import { Submission, SubmissionData } from './submission';
import DataLoader = require('dataloader');

export const evaluationSchema = gql`
    type Evaluation {
        id: ID!

        submission: Submission!
    }
`;

/** An evaluation of a submission */
@Table({ tableName: 'evaluations' })
export class EvaluationData extends UuidBaseModel<EvaluationData> {
    @AllowNull(false)
    @Column
    submissionId!: string;

    @AllowNull(false)
    @Column
    eventsJson!: string;

    @AllowNull(false)
    @Column
    problemArchiveHash!: string;
}

export class Evaluation implements ApiOutputValue<'Evaluation'> {
    __typename = 'Evaluation' as const;

    constructor(readonly id: string, readonly ctx: ApiContext) {}

    async getData() {
        return this.ctx.cache(EvaluationCache).byId.load(this.id);
    }

    async submission() {
        return new Submission((await this.getData()).submissionId, this.ctx);
    }

    async problemArchiveHash() {
        return (await this.getData()).problemArchiveHash;
    }

    async getObjectiveOutcomes() {
        const outcomes = await this.ctx.cache(OutcomeCache).byEvaluation.load(this.id);
        const material = await this.getProblemMaterial();

        return new Map(
            material.objectives.map((objective, objectiveIndex) => [
                objective,
                outcomes.find(a => a.objectiveIndex === objectiveIndex) ?? null,
            ]),
        );
    }

    async getOutcome(objective: ObjectiveDefinition) {
        const outcomes = [...(await this.getObjectiveOutcomes()).entries()];
        const objectiveOutcome = outcomes.find(([{ id }]) => id === objective.id);
        if (!objectiveOutcome) return null;
        const [, outcome] = objectiveOutcome;
        return outcome;
    }

    private async getProblemMaterial() {
        const submission = await this.submission();
        return submission.getProblemMaterial();
    }

    async events() {
        const data = await this.getData();
        return JSON.parse(data.eventsJson) as UIMessage[];
    }

    async getTotalScore() {
        return getTotalScoreFromOutcomes(await this.getProblemMaterial(), await this.getObjectiveOutcomes());
    }
}

export class EvaluationCache extends ApiCache {
    byId = createByIdDataLoader(this.ctx, EvaluationData);
    bySubmission = createSimpleLoader((submissionId: string) =>
        this.ctx.table(EvaluationData).findAll({
            where: { submissionId },
        }),
    );
    officialBySubmission = new DataLoader((submissionIds: readonly string[]) =>
        Promise.all(
            submissionIds.map(
                async submissionId =>
                    this.ctx.table(EvaluationData).findOne({
                        where: { submissionId },
                        order: [['createdAt', 'DESC']],
                    }) ?? null,
            ),
        ),
    );
    all = createSimpleLoader((unused: '') => this.ctx.table(EvaluationData).findAll());
}

function getTotalScoreFromOutcomes(material: ProblemMaterial, outcomes: Map<ObjectiveDefinition, OutcomeData | null>) {
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
