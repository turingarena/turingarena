import { gql } from 'apollo-server-core';
import { AllowNull, BelongsTo, Column, ForeignKey, HasMany, Table } from 'sequelize-typescript';
import { BaseModel } from '../main/base-model';
import { Achievement } from './achievement';
import { EvaluationEvent } from './evaluation-event';
import { Submission } from './submission';

export const evaluationSchema = gql`
    type Evaluation {
        submission: Submission!
        events: [EvaluationEvent!]!
        status: EvaluationStatus!
    }

    type EvaluationEvent {
        evaluation: Evaluation!
        data: String!
    }

    "Status of an evaluation"
    enum EvaluationStatus {
        "The evaluation is not completed yet"
        PENDING
        "The evaluation terminated correctly"
        SUCCESS
        "There was an error in this evaluation"
        ERROR
    }
`;

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
    getSubmission!: () => Promise<Submission>;

    /** Events of this submission */
    @HasMany(() => EvaluationEvent)
    events!: EvaluationEvent[];
    getEvents!: () => Promise<EvaluationEvent[]>;

    /** Achievements of this submission */
    @HasMany(() => Achievement)
    achievements!: Achievement[];
    getAchievements!: () => Promise<Achievement[]>;
}

/** Status of this submission */
export enum EvaluationStatus {
    /** The evaluation not completed yet */
    PENDING = 'PENDING',
    /** The evaluation terminated correclty */
    SUCCESS = 'SUCCESS',
    /** There was an error in this evaluation */
    ERROR = 'ERROR',
}
