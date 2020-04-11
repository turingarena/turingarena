import { gql } from 'apollo-server-core';
import { AllowNull, Column, DataType, HasMany, Index, Table, Unique } from 'sequelize-typescript';
import { ApiObject } from '../main/api';
import { createSimpleLoader, UuidBaseModel } from '../main/base-model';
import { Resolvers } from '../main/resolver-types';
import { ContestProblemAssignment } from './contest-problem-assignment';
import { ScoreGradeDomain } from './feedback/score';
import { ProblemMaterial } from './material/problem-material';
import { getProblemTaskInfo } from './material/problem-task-info';

export const problemSchema = gql`
    type Problem {
        name: ID!
        fileCollection: FileCollection
    }

    input ProblemInput {
        name: ID!
        files: [ID!]!
    }
`;

/** A problem in TuringArena. */
@Table
export class Problem extends UuidBaseModel<Problem> {
    /** Name of the problem, must be a valid identifier. */
    @Unique
    @Column
    @Index
    name!: string;

    /** Contests that contains this problem */
    @HasMany(() => ContestProblemAssignment)
    contestAssigments!: ContestProblemAssignment[];

    /** Files collection that belongs to this problem. */
    @AllowNull(false)
    @Column(DataType.UUIDV4)
    fileCollectionId!: string;

    async getTaskInfo() {
        return getProblemTaskInfo(this);
    }

    async getMaterial() {
        const taskInfo = await this.getTaskInfo();

        return new ProblemMaterial(this, taskInfo);
    }
}

export interface ProblemModelRecord {
    Problem: Problem;
}

export class ProblemApi extends ApiObject {
    byName = createSimpleLoader((name: string) => this.ctx.root.table(Problem).findOne({ where: { name } }));
}

export const problemResolvers: Resolvers = {
    Problem: {
        fileCollection: problem => ({ uuid: problem.fileCollectionId }),
        name: p => p.name,

        title: async p => (await p.getMaterial()).title,
        statement: async p => (await p.getMaterial()).statement,
        attachments: async p => (await p.getMaterial()).attachments,
        awards: async p => (await p.getMaterial()).awards,
        submissionFields: async p => (await p.getMaterial()).submissionFields,
        submissionFileTypes: async p => (await p.getMaterial()).submissionFileTypes,
        submissionFileTypeRules: async p => (await p.getMaterial()).submissionFileTypeRules,
        submissionListColumns: async p => (await p.getMaterial()).submissionListColumns,
        evaluationFeedbackColumns: async p => (await p.getMaterial()).evaluationFeedbackColumns,
        totalScoreDomain: async p => new ScoreGradeDomain((await p.getMaterial()).scoreRange),
    },
};
