import { gql } from 'apollo-server-core';
import { DateTime } from 'luxon';
import { AllowNull, Column, DataType, ForeignKey, HasMany, Index, Table, Unique } from 'sequelize-typescript';
import { __generated_ContestStatus } from '../generated/graphql-types';
import { BaseModel } from '../main/base-model';
import { ModelRoot } from '../main/model-root';
import { Resolvers } from '../main/resolver-types';
import { ContestProblemAssignment } from './contest-problem-assignment';
import { ContestProblemSet } from './contest-problem-set';
import { FileCollection } from './file-collection';
import { ProblemMaterial } from './material/problem-material';
import { Participation } from './participation';
import { Problem } from './problem';
import { User } from './user';

export const contestSchema = gql`
    type Contest {
        name: ID!
        title: Text!
        start: String!
        end: String!
        status: ContestStatus!
        problemSet: ContestProblemSet!
    }

    input ContestInput {
        name: ID!
        title: String!
        start: String!
        end: String!
    }

    enum ContestStatus {
        NOT_STARTED
        RUNNING
        ENDED
    }
`;

/** A contest in TuringArena */
@Table
export class Contest extends BaseModel<Contest> {
    /** Name of the contest, must be a valid identifier, e.g. ioi */
    @Unique
    @Index
    @AllowNull(false)
    @Column
    name!: string;

    /** Title of the contest, as a string, e.g. 'International Olimpics in Informatics' */
    @AllowNull(false)
    @Column
    title!: string;

    /** When the contest will start */
    @AllowNull(false)
    @Column
    start!: Date;

    /** When the contest will end */
    @AllowNull(false)
    @Column
    end!: Date;

    @AllowNull(false)
    @Column(DataType.UUIDV4)
    @ForeignKey(() => FileCollection)
    fileCollectionId!: string;

    /** The list of problems in this contest */
    @HasMany(() => ContestProblemAssignment)
    problemAssignments!: ContestProblemAssignment[];
    createProblemAssignment!: (problem: object, options?: object) => Promise<ContestProblemAssignment>;
    getProblemAssignments!: () => Promise<ContestProblemAssignment[]>;

    /** The list of users in this contest */
    @HasMany(() => Participation)
    participations!: Participation[];
    getParticipations!: (options: object) => Promise<Participation[]>;
    createParticipation!: (participation: object, options: object) => Promise<Participation>;
    addParticipation!: (options: object) => Promise<unknown>;

    getStatus(): ContestStatus {
        const start = DateTime.fromJSDate(this.start).valueOf();
        const end = DateTime.fromJSDate(this.end).valueOf();
        const now = DateTime.local().valueOf();

        if (now < start) return 'NOT_STARTED';
        else if (now < end) return 'RUNNING';
        else return 'NOT_STARTED';
    }

    async getProblemSetMaterial(): Promise<ProblemMaterial[]> {
        return Promise.all((await this.getProblemAssignments()).map(async a => (await a.getProblem()).getMaterial()));
    }
}

export type ContestStatus = __generated_ContestStatus;

export interface MutationModelRecord {
    Mutation: ModelRoot;
}

export const contestMutationResolvers: Resolvers = {
    Mutation: {
        addProblem: async (root, { contestName, name }) => {
            const contest =
                (await root.table(Contest).findOne({
                    where: { name: contestName },
                })) ?? root.fail(`no such contest '${contestName}'`);
            const problem =
                (await root.table(Problem).findOne({ where: { name } })) ?? root.fail(`no such problem '${name}'`);
            await contest.createProblemAssignment({
                problem,
            });

            return true;
        },
        addUser: async (root, { contestName, username }) => {
            const contest =
                (await root.table(Contest).findOne({
                    where: { name: contestName },
                })) ?? root.fail(`no such contest '${contestName}'`);
            const user =
                (await root.table(User).findOne({ where: { username } })) ?? root.fail(`no such user '${username}'`);
            await contest.addParticipation(user);

            return true;
        },
    },
};

export interface ContestModelRecord {
    Contest: Contest;
}

export const contestResolvers: Resolvers = {
    Contest: {
        title: contest => [{ value: contest.title }],
        start: contest => DateTime.fromJSDate(contest.start).toISO(),
        end: contest => DateTime.fromJSDate(contest.end).toISO(),
        status: contest => contest.getStatus(),
        problemSet: contest => new ContestProblemSet(contest),
    },
};
