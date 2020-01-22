import { AllowNull, BelongsTo, Column, ForeignKey, HasMany, Table } from 'sequelize-typescript';
import { BaseModel } from '../main/base-model';
import { EvaluationEvent } from './evaluation-event';
import { Submission } from './submission';

/** An evaluation of a submission */
@Table
export class Evaluation extends BaseModel<Evaluation> {
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
