import { gql } from 'apollo-server-core';
import {
    Column,
    HasMany,
    Index,
    Model,
    Table,
    Unique,
} from 'sequelize-typescript';
import { FindOptions } from 'sequelize/types';
import { Resolvers } from '../generated/graphql-types';
import { ContestProblem } from './contest-problem';
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
    @HasMany(() => ContestProblem)
    contestProblems: ContestProblem[];

    /** Files that belongs to this problem. */
    @HasMany(() => ProblemFile)
    files: ProblemFile[];
    getFiles: (options: FindOptions) => Promise<ProblemFile[]>;
    findFile: (options: object) => Promise<ProblemFile>;
    createFile: (file: object, options?: object) => Promise<ProblemFile>;
}

export const problemResolvers: Resolvers = {
    Problem: {
        files: problem => problem.getFiles(),
    },
};
