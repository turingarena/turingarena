import { gql } from 'apollo-server-core';
import { AllowNull, BelongsTo, Column, ForeignKey, PrimaryKey, Table } from 'sequelize-typescript';
import { BaseModel } from '../main/base-model';
import { Evaluation } from './evaluation';
import { FulfillmentGrade } from './feedback/fulfillment';
import { ScoreGrade, ScoreGradeDomain } from './feedback/score';

export const achievementSchema = gql`
    type Achievement {
        evaluation: Submission!
        awardAssignment: ContestAwardAssignment!
        grade: GradeValue!
    }
`;

/** An evaluation of a submission */
@Table
export class Achievement extends BaseModel<Achievement> {
    @PrimaryKey
    @ForeignKey(() => Evaluation)
    @AllowNull(false)
    @Column
    evaluationId!: number;

    @PrimaryKey
    @AllowNull(false)
    @Column
    awardIndex!: number;

    @Column
    grade!: number;

    @BelongsTo(() => Evaluation, 'evaluationId')
    evaluation!: Evaluation;
    getEvaluation!: () => Promise<Evaluation>;

    async getAward() {
        const evaluation = await this.getEvaluation();
        const submission = await evaluation.getSubmission();
        const problem = await submission.getProblem();
        const material = await problem.getMaterial();

        return material.awards[this.awardIndex];
    }

    getScoreGrade({ scoreRange }: ScoreGradeDomain): ScoreGrade {
        return new ScoreGrade(scoreRange, this.grade);
    }

    getFulfillmentGrade(): FulfillmentGrade {
        return new FulfillmentGrade(this.grade === 1);
    }
}

export interface AchievementModelRecord {
    Achievement: Achievement;
}
