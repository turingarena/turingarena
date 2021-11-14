import { gql } from 'apollo-server-core';
import { AllowNull, Column, ForeignKey, Table } from 'sequelize-typescript';
import { ApiCache } from '../main/api-cache';
import { ApiContext } from '../main/api-context';
import { createByIdDataLoader, createSimpleLoader, UuidBaseModel } from '../main/base-model';
import { ApiOutputValue } from '../main/graphql-types';
import { Submission, SubmissionData } from './submission';

export const evaluationSchema = gql`
    type Evaluation {
        id: ID!

        submission: Submission!
        status: EvaluationStatus!
    }

    "Status of an evaluation"
    enum EvaluationStatus {
        "The evaluation is not completed yet"
        PENDING
        "The evaluation terminated correctly"
        SUCCESS
        "There was an error in this evaluation"
        ERROR
        "There was an error in the compilation"
        COMPILEERROR
    }
`;

/** An evaluation of a submission */
@Table({ tableName: 'evaluations' })
export class EvaluationData extends UuidBaseModel<EvaluationData> {
    @ForeignKey(() => SubmissionData)
    @AllowNull(false)
    @Column
    submissionId!: string;

    /** Status of this evaluation */
    @AllowNull(false)
    @Column
    status!: EvaluationStatus;
}

export class Evaluation implements ApiOutputValue<'Evaluation'> {
    __typename = 'Evaluation' as const;

    constructor(readonly id: string, readonly ctx: ApiContext) {}

    async getData() {
        return this.ctx.cache(EvaluationCache).byId.load(this.id);
    }

    async status() {
        return (await this.getData()).status;
    }

    async submission() {
        return new Submission((await this.getData()).submissionId, this.ctx);
    }
}

/** Status of this submission */
export enum EvaluationStatus {
    /** The evaluation not completed yet */
    PENDING = 'PENDING',
    /** The evaluation terminated correclty */
    SUCCESS = 'SUCCESS',
    /** There was an error in this evaluation */
    ERROR = 'ERROR',
    /** There was an error in the compilation */
    COMPILEERROR = 'COMPILEERROR',
}

export class EvaluationCache extends ApiCache {
    byId = createByIdDataLoader(this.ctx, EvaluationData);
    allBySubmissionId = createSimpleLoader((submissionId: string) =>
        this.ctx.table(EvaluationData).findAll({
            where: { submissionId },
        }),
    );
    officialOf = createSimpleLoader((submissionId: string) =>
        this.ctx.table(EvaluationData).findOne({
            where: { submissionId },
            order: [['createdAt', 'DESC']],
        }),
    );
}
