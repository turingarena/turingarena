import { DataTypes } from 'sequelize';
import { BelongsTo, Column, ForeignKey, HasMany, Model, Table } from 'sequelize-typescript';
import { Submission } from './submission';

/** An evaluation of a submission */
@Table
export class Evaluation extends Model<Evaluation> {
    @ForeignKey(() => Submission)
    @Column
    submissionId!: number;

    /** Status of this evaluation */
    @Column
    status!: EvaluationStatus;

    /** True if the evaluation should be considered official for ranking purposes */
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
    @Column
    evaluationId!: number;

    /** Evaluation to which this event belongs to */
    @BelongsTo(() => Evaluation, 'evaluationId')
    evaluation: Evaluation;

    /** Data of this event, in a backend-specific format */
    @Column(DataTypes.JSON)
    data!: object;
}
