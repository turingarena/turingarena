import { DataTypes } from 'sequelize';
import { AllowNull, BelongsTo, Column, ForeignKey, HasMany, Model, Table } from 'sequelize-typescript';
import { Submission } from './submission';

/** An evaluation of a submission */
@Table
export class Evaluation extends Model<Evaluation> {
    @ForeignKey(() => Submission)
    @AllowNull(false)
    @Column
    submissionId!: number;

    /** Status of this evaluation */
    @AllowNull(false)
    @Column
    status!: EvaluationStatus;

    /** True if the evaluation should be considered official for ranking purposes */
    @AllowNull(false)
    @Column
    isOfficial!: boolean;

    /** Submission to which this evaluation belongs to */
    @BelongsTo(() => Submission, 'submissionId')
    submission!: Submission;

    /** Events of this submission */
    @HasMany(() => EvaluationEvent)
    events!: EvaluationEvent[];
}

/** Status of this submission */
export enum EvaluationStatus {
    /** The evaluation is received and ready to be evaluated */
    PENDING,
    /** The evaluation started */
    EVALUATING,
    /** The evaluation terminated correclty */
    SUCCESS,
    /** There was an error in this evaluation */
    ERROR,
}

/** Evant of an evaluation */
@Table({ updatedAt: false })
export class EvaluationEvent extends Model<EvaluationEvent> {
    @ForeignKey(() => Evaluation)
    @AllowNull(false)
    @Column
    evaluationId!: number;

    /** Evaluation to which this event belongs to */
    @BelongsTo(() => Evaluation, 'evaluationId')
    evaluation: Evaluation;

    /** Data of this event, in a backend-specific format */
    @AllowNull(false)
    @Column(DataTypes.JSON)
    data!: object;
}
