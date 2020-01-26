import { gql } from 'apollo-server-core';
import { AllowNull, BelongsTo, Column, ForeignKey, PrimaryKey, Table } from 'sequelize-typescript';
import { BaseModel } from '../main/base-model';
import { Evaluation } from './evaluation';

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
    subtaskIndex!: number;

    @Column
    grade!: number;

    @BelongsTo(() => Evaluation, 'evaluationId')
    evaluation!: Evaluation;
}
