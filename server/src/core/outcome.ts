import { gql } from 'apollo-server-core';
import { AllowNull, Column, Table } from 'sequelize-typescript';
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

@Table({ tableName: 'outcomes', indexes: [{ fields: ['problem_id', 'user_id', 'objective_index', 'grade'] }] })
export class OutcomeData extends BaseModel<OutcomeData> {
    @AllowNull(false)
    @Column
    problemId!: string;

    @AllowNull(false)
    @Column
    userId!: string;

    @AllowNull(false)
    @Column
    submissionId!: string;

    @AllowNull(false)
    @Column
    submittedAt!: Date;

    @AllowNull(false)
    @Column
    problemHash!: string;

    @AllowNull(false)
    @Column
    evaluationId!: string;

    @AllowNull(false)
    @Column
    evaluatedAt!: Date;

    @AllowNull(false)
    @Column
    objectiveIndex!: number; // TODO: should be objective ID

    @AllowNull(false)
    @Column
    grade!: number;

    @AllowNull(false)
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
