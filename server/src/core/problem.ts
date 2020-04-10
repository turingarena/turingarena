import { gql } from 'apollo-server-core';
import { AllowNull, Column, DataType, HasMany, Index, Table, Unique } from 'sequelize-typescript';
import { UuidBaseModel } from '../main/base-model';
import { Resolvers } from '../main/resolver-types';
import { ContestProblemAssignment } from './contest-problem-assignment';
import { ProblemMaterial, problemMaterialResolversExtensions } from './material/problem-material';
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

export const problemResolvers: Resolvers = {
    Problem: {
        fileCollection: problem => ({ uuid: problem.fileCollectionId }),
        ...problemMaterialResolversExtensions.Problem,
    },
};
