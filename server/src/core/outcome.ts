import { gql } from 'apollo-server-core';
import { Column, Table } from 'sequelize-typescript';
import { ApiCache } from '../main/api-cache';
import { ApiContext } from '../main/api-context';
import { BaseModel, createSimpleLoader } from '../main/base-model';
import { FulfillmentGrade } from './data/fulfillment';
import { ScoreGrade, ScoreGradeDomain } from './data/score';
import { EvaluationCache } from './evaluation';
import { ProblemMaterialCache } from './problem-definition-material';
import { Submission } from './submission';

export const outcomeSchema = gql`
    """
    A grade obtained by a submission for a certain objective of a problem.
    """
    type Outcome {
        submission: Submission!
        objective: ObjectiveInstance!
        grade: Grade!
    }
`;

@Table({ tableName: 'outcomes' })
export class OutcomeData extends BaseModel<OutcomeData> {
    @Column
    problemId!: string;

    @Column
    userId!: string;

    @Column
    submissionId!: string;

    @Column
    submittedAt!: Date;

    @Column
    problemHash!: string;

    @Column
    evaluationId!: string;

    @Column
    evaluatedAt!: Date;

    @Column
    objectiveIndex!: number; // TODO: should be objective ID

    @Column
    grade!: number;

    @Column
    isRanked!: boolean;

    getScoreGrade({ scoreRange }: ScoreGradeDomain): ScoreGrade {
        return new ScoreGrade(scoreRange, this.grade);
    }

    async getObjective(ctx: ApiContext) {
        const evaluation = await ctx.cache(EvaluationCache).byId.load(this.evaluationId);
        const submission = Submission.fromId(evaluation.submissionId, ctx);
        const { instance } = await submission.getUndertaking();
        const material = await ctx.cache(ProblemMaterialCache).byId.load(instance.definition.id);

        return material.objectives[this.objectiveIndex];
    }

    getFulfillmentGrade(): FulfillmentGrade {
        return new FulfillmentGrade(this.grade === 1);
    }
}

export class OutcomeCache extends ApiCache {
    byEvaluation = createSimpleLoader((evaluationId: string) =>
        this.ctx.table(OutcomeData).findAll({
            where: { evaluationId },
        }),
    );
}
