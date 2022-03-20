import { gql } from 'apollo-server-core';
import { AllowNull, Column, ForeignKey, Table } from 'sequelize-typescript';
import { ApiCache } from '../main/api-cache';
import { ApiContext } from '../main/api-context';
import { createByIdDataLoader, createSimpleLoader, UuidBaseModel } from '../main/base-model';
import { ApiOutputValue } from '../main/graphql-types';
import { Submission, SubmissionData } from './submission';
import DataLoader = require('dataloader');

export const evaluationSchema = gql`
    type Evaluation {
        id: ID!

        submission: Submission!
    }
`;

/** An evaluation of a submission */
@Table({ tableName: 'evaluations' })
export class EvaluationData extends UuidBaseModel<EvaluationData> {
    @ForeignKey(() => SubmissionData)
    @AllowNull(false)
    @Column
    submissionId!: string;

    @AllowNull(false)
    @Column
    eventsJson!: string;

    @AllowNull(false)
    @Column
    problemArchiveHash!: string;
}

export class Evaluation implements ApiOutputValue<'Evaluation'> {
    __typename = 'Evaluation' as const;

    constructor(readonly id: string, readonly ctx: ApiContext) {}

    async getData() {
        return this.ctx.cache(EvaluationCache).byId.load(this.id);
    }

    async submission() {
        return new Submission((await this.getData()).submissionId, this.ctx);
    }

    async problemArchiveHash() {
        return (await this.getData()).problemArchiveHash;
    }
}

export class EvaluationCache extends ApiCache {
    byId = createByIdDataLoader(this.ctx, EvaluationData);
    bySubmission = createSimpleLoader((submissionId: string) =>
        this.ctx.table(EvaluationData).findAll({
            where: { submissionId },
        }),
    );
    officialBySubmission = new DataLoader((submissionIds: readonly string[]) =>
        Promise.all(
            submissionIds.map(
                async submissionId =>
                    this.ctx.table(EvaluationData).findOne({
                        where: { submissionId },
                        order: [['createdAt', 'DESC']],
                    }) ?? null,
            ),
        ),
    );
    all = createSimpleLoader((unused: '') => this.ctx.table(EvaluationData).findAll());
}
