import { gql } from 'apollo-server-core';
import { AllowNull, Column, ForeignKey, PrimaryKey, Table } from 'sequelize-typescript';
import { ApiObject } from '../main/api';
import { BaseModel } from '../main/base-model';
import { Evaluation, EvaluationApi } from './evaluation';
import { FulfillmentGrade } from './feedback/fulfillment';
import { ScoreGrade, ScoreGradeDomain } from './feedback/score';
import { ProblemApi } from './problem';
import { SubmissionApi } from './submission';

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
}

export interface AchievementModelRecord {
    Achievement: Achievement;
}

export class AchievementApi extends ApiObject {
    async getAward(a: Achievement) {
        const evaluation = await this.ctx.api(EvaluationApi).byId.load(a.evaluationId);
        const submission = await this.ctx.api(SubmissionApi).byId.load(evaluation.submissionId);
        const problem = await this.ctx.api(ProblemApi).byId.load(submission.problemId);
        const material = await problem.getMaterial();

        return material.awards[a.awardIndex];
    }

    getScoreGrade(a: Achievement, { scoreRange }: ScoreGradeDomain): ScoreGrade {
        return new ScoreGrade(scoreRange, a.grade);
    }

    getFulfillmentGrade(a: Achievement): FulfillmentGrade {
        return new FulfillmentGrade(a.grade === 1);
    }
}
