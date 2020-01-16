import { gql } from 'apollo-server-core';
import {
    AutoIncrement,
    BelongsToMany,
    Column,
    ForeignKey,
    HasMany, Index,
    IsUUID,
    Model,
    PrimaryKey,
    Table,
    Unique,
} from 'sequelize-typescript';
import { Resolvers } from '../generated/graphql-types';
import { File } from './file';
import { Problem } from './problem';
import { User } from './user';

export const contestSchema = gql`
    type Contest {
        name: ID!
        title: String!
        start: String!
        end: String!
    }

    type ContestMutations {
        addProblem(name: ID!): Boolean
        removeProblem(name: ID!): Boolean
        addUser(username: ID!): Boolean
        removeUser(username: ID!): Boolean
    }

    input ContestInput {
        name: ID!
        title: String!
        start: String!
        end: String!
    }
`;

@Table({timestamps: false})
export class Participation extends Model<Participation> {
    @ForeignKey(() => User)
    @PrimaryKey
    @Column
    userId!: number;

    @ForeignKey(() => Contest)
    @PrimaryKey
    @Column
    contestId!: number;
}

@Table({timestamps: false})
export class ContestProblem extends Model<ContestProblem> {
    @ForeignKey(() => Problem)
    @PrimaryKey
    @Column
    problemId!: number;

    @ForeignKey(() => Contest)
    @PrimaryKey
    @Column
    contestId!: number;
}

@Table({ timestamps: false })
export class ContestFile extends Model<ContestFile> {
    @ForeignKey(() => Contest)
    @PrimaryKey
    @Column
    contestId!: number;

    @ForeignKey(() => File)
    @PrimaryKey
    @Column
    fileId!: number;
}

@Table
export class Contest extends Model<Contest> {
    @PrimaryKey
    @AutoIncrement
    @Column
    id!: number;

    @Unique
    @Index
    @Column
    name!: string;

    @Column
    title!: string;

    @Column
    start!: Date;

    @Column
    end!: Date;

    @BelongsToMany(() => Problem, () => ContestProblem)
    problems!: Problem[];

    @BelongsToMany(() => User, () => Participation)
    users!: User[];

    @BelongsToMany(() => File, () => ContestFile)
    files!: File[];
}

export const contestResolvers: Resolvers = {
    Contest: {
        // TODO: resolver for start and end to return in correct ISO format
    },
    ContestMutations: {
        addProblem: async ({contest}, {name}, ctx) => {
            const problem = await ctx.db.Problem.findOne({ where: { name } });
            await contest.addProblem(problem);

            return true;
        },
        addUser: async ({contest}, {username}, ctx) => {
            const user = await ctx.db.User.findOne({ where: { username }});
            await contest.addUser(user);

            return true;
        },
    },
};
