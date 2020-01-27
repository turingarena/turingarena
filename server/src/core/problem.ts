import { gql } from 'apollo-server-core';
import { Column, HasMany, Index, Table, Unique } from 'sequelize-typescript';
import { FindOptions } from 'sequelize/types';
import { BaseModel } from '../main/base-model';
import { Resolvers } from '../main/resolver-types';
import { ContestProblemAssignment } from './contest-problem-assignment';
import { ProblemMaterial, problemMaterialResolversExtensions } from './material/problem-material';
import { getProblemTaskInfo } from './material/problem-task-info';
import { ProblemFile } from './problem-file';

export const problemSchema = gql`
    type Problem {
        name: ID!
        files: [ProblemFile!]!
    }

    input ProblemInput {
        name: ID!
        files: [ID!]!
    }
`;

/** A problem in TuringArena. */
@Table
export class Problem extends BaseModel<Problem> {
    /** Name of the problem, must be a valid identifier. */
    @Unique
    @Column
    @Index
    name!: string;

    /** Contests that contains this problem */
    @HasMany(() => ContestProblemAssignment)
    contestAssigments!: ContestProblemAssignment[];

    /** Files that belongs to this problem. */
    @HasMany(() => ProblemFile)
    files!: ProblemFile[];
    getFiles!: (options?: FindOptions) => Promise<ProblemFile[]>;
    findFile!: (options?: object) => Promise<ProblemFile>;
    createFile!: (file: object, options?: object) => Promise<ProblemFile>;

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
        files: problem => problem.getFiles(),
        ...problemMaterialResolversExtensions.Problem,
    },
};
