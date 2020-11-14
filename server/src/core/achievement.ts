import { gql } from 'apollo-server-core';
import { AllowNull, Column, ForeignKey, PrimaryKey, Table } from 'sequelize-typescript';
import { ApiObject } from '../main/api';
import { ApiContext } from '../main/api-context';
import { BaseModel, createSimpleLoader } from '../main/base-model';
import { Evaluation, EvaluationApi } from './evaluation';
import { FulfillmentGrade } from './feedback/fulfillment';
import { ScoreGrade, ScoreGradeDomain } from './feedback/score';
import { ProblemMaterialApi } from './material/problem-material';
import { Submission } from './submission';

export const achievementSchema = gql`
    type Achievement {
        evaluation: Submission!
        awardAssignment: ContestAwardAssignment!
        grade: Grade!
    }
`;

/** An evaluation of a submission */
@Table
export class Achievement extends BaseModel<Achievement> {
    @PrimaryKey
    @ForeignKey(() => Evaluation)
    @AllowNull(false)
    @Column
    evaluationId!: string;

    @PrimaryKey
    @AllowNull(false)
    @Column
    awardIndex!: number;

    @Column
    grade!: number;

    getScoreGrade({ scoreRange }: ScoreGradeDomain): ScoreGrade {
        return new ScoreGrade(scoreRange, this.grade);
    }

    async getAward(ctx: ApiContext) {
        const evaluation = await ctx.api(EvaluationApi).byId.load(this.evaluationId);
        const submission = Submission.fromId(evaluation.submissionId);
        const { assignment } = await submission.getTackling(ctx);
        const material = await ctx.api(ProblemMaterialApi).dataLoader.load(assignment.problem);

        return material.awards[this.awardIndex];
    }

    getFulfillmentGrade(): FulfillmentGrade {
        return new FulfillmentGrade(this.grade === 1);
    }
}

export interface AchievementModelRecord {
    Achievement: Achievement;
}

export class AchievementApi extends ApiObject {
    allByEvaluationId = createSimpleLoader((evaluationId: string) =>
        this.ctx.table(Achievement).findAll({
            where: { evaluationId },
        }),
    );
}
