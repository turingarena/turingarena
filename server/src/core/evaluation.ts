import { gql } from 'apollo-server-core';
import { AllowNull, Column, ForeignKey, HasMany, Table } from 'sequelize-typescript';
import { ApiObject } from '../main/api';
import { createByIdLoader, UuidBaseModel } from '../main/base-model';
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
export class Evaluation extends UuidBaseModel<Evaluation> {
    @ForeignKey(() => Submission)
    @AllowNull(false)
    @Column
    submissionId!: string;

    /** Status of this evaluation */
    @AllowNull(false)
    @Column
    status!: EvaluationStatus;

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

export interface EvaluationModelRecord {
    Evaluation: Evaluation;
}

export class EvaluationApi extends ApiObject {
    byId = createByIdLoader(this.ctx, Evaluation);
}
