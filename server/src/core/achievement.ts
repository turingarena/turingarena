import { gql } from 'apollo-server-core';
import { AllowNull, Column, ForeignKey, PrimaryKey, Table } from 'sequelize-typescript';
import { ApiCache } from '../main/api-cache';
import { ApiContext } from '../main/api-context';
import { BaseModel, createSimpleLoader } from '../main/base-model';
import { EvaluationCache, EvaluationData } from './evaluation';
import { FulfillmentGrade } from './feedback/fulfillment';
import { ScoreGrade, ScoreGradeDomain } from './feedback/score';
import { ProblemMaterialCache } from './material/problem-material';
import { Submission } from './submission';

export const achievementSchema = gql`
    type Achievement {
        evaluation: Submission!
        objectiveAssignment: ObjectiveInstance!
        grade: Grade!
    }
`;

/** An evaluation of a submission */
@Table
export class Achievement extends BaseModel<Achievement> {
    @PrimaryKey
    @ForeignKey(() => EvaluationData)
    @AllowNull(false)
    @Column
    evaluationId!: string;

    @PrimaryKey
    @AllowNull(false)
    @Column
    objectiveIndex!: number;

    @Column
    grade!: number;

    getScoreGrade({ scoreRange }: ScoreGradeDomain): ScoreGrade {
        return new ScoreGrade(scoreRange, this.grade);
    }

    async getObjective(ctx: ApiContext) {
        const evaluation = await ctx.cache(EvaluationCache).byId.load(this.evaluationId);
        const submission = Submission.fromId(evaluation.submissionId, ctx);
        const { assignment } = await submission.getTackling();
        const material = await ctx.cache(ProblemMaterialCache).byId.load(assignment.problem.id());

        return material.objectives[this.objectiveIndex];
    }

    getFulfillmentGrade(): FulfillmentGrade {
        return new FulfillmentGrade(this.grade === 1);
    }
}

export class AchievementCache extends ApiCache {
    byEvaluation = createSimpleLoader((evaluationId: string) =>
        this.ctx.table(Achievement).findAll({
            where: { evaluationId },
        }),
    );
}
