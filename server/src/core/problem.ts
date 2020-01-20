import { gql } from 'apollo-server-core';
import { Column, HasMany, Index, Model, Table, Unique } from 'sequelize-typescript';
import { FindOptions } from 'sequelize/types';
import { ResolversWithModels } from '../main/resolver-types';
import { ContestProblemSetItem } from './contest-problem-set-item';
import { problemMaterialResolversExtensions } from './material/problem-material';
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
export class Problem extends Model<Problem> {
    /** Name of the problem, must be a valid identifier. */
    @Unique
    @Column
    @Index
    name!: string;

    /** Contests that contains this problem */
    @HasMany(() => ContestProblemSetItem)
    contestProblems!: ContestProblemSetItem[];

    /** Files that belongs to this problem. */
    @HasMany(() => ProblemFile)
    files!: ProblemFile[];
    getFiles!: (options?: FindOptions) => Promise<ProblemFile[]>;
    findFile!: (options?: object) => Promise<ProblemFile>;
    createFile!: (file: object, options?: object) => Promise<ProblemFile>;
}

export const problemResolvers: ResolversWithModels<{
    Problem: Problem;
}> = {
    Problem: {
        files: problem => problem.getFiles(),
        ...problemMaterialResolversExtensions.Problem,
    },
};
