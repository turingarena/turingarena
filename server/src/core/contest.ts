import { gql } from 'apollo-server-core';
import { DateTime } from 'luxon';
import * as mime from 'mime-types';
import { Op } from 'sequelize';
import { AllowNull, Column, DataType, ForeignKey, HasMany, Index, Table, Unique } from 'sequelize-typescript';
import { __generated_ContestStatus } from '../generated/graphql-types';
import { UuidBaseModel } from '../main/base-model';
import { ModelRoot } from '../main/model-root';
import { Resolvers } from '../main/resolver-types';
import { ContestProblemAssignment } from './contest-problem-assignment';
import { ContestProblemSet } from './contest-problem-set';
import { FileCollection } from './file-collection';
import { Media, MediaVariant } from './material/media';
import { ProblemMaterial } from './material/problem-material';
import { Participation } from './participation';
import { Problem } from './problem';
import { User } from './user';

export const contestSchema = gql`
    type Contest {
        name: ID!
        title: Text!

        "Statement of this contest, presented as its home page"
        statement: Media!

        start: String!
        end: String!
        status: ContestStatus!
        problemSet: ContestProblemSet!
        fileCollection: FileCollection!
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
export class Contest extends UuidBaseModel<Contest> {
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

    /** supported languages, e.g [C, C++, Python2] */
    @Column(DataType.JSON)
    languages!: string[];

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

    private statementVariantFromFile(archiveFile: FileCollection): MediaVariant {
        const type = mime.lookup(archiveFile.path);

        return {
            name: archiveFile.path,
            type: type !== false ? type : 'application/octet-stream',
            content: () => archiveFile.getContent(),
        };
    }

    async getStatement(): Promise<Media> {
        const statementFiles = await this.root.table(FileCollection).findAll({
            where: {
                uuid: this.fileCollectionId,
                path: {
                    [Op.like]: 'home%',
                },
            },
        });

        return statementFiles.map((archiveFile): MediaVariant => this.statementVariantFromFile(archiveFile));
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
        fileCollection: contest => ({ uuid: contest.fileCollectionId }),
        statement: contest => contest.getStatement(),
    },
};
