import { gql } from 'apollo-server-core';
import { Column, HasMany, Index, Table, Unique } from 'sequelize-typescript';
import { FindOptions } from 'sequelize/types';
import { BaseModel } from '../main/base-model';
import { ResolversWithModels } from '../main/resolver-types';
import { ContestProblemAssignment } from './contest-problem-assignment';
import { problemMaterialResolversExtensions } from './material/problem-material';
import { getProblemTaskInfo, ProblemTaskInfo } from './material/problem-task-info';
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

    taskInfoCache?: ProblemTaskInfo;
    async getTaskInfo() {
        return getProblemTaskInfo(this);
    }
}

export const problemResolvers: ResolversWithModels<{
    Problem: Problem;
}> = {
    Problem: {
        files: problem => problem.getFiles(),
        ...problemMaterialResolversExtensions.Problem,
    },
};
