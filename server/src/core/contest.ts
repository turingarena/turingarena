import { gql } from 'apollo-server-core';
import * as fs from 'fs';
import { DateTime } from 'luxon';
import * as path from 'path';
import {
    AllowNull,
    Column,
    HasMany,
    Index,
    Model,
    Table,
    Unique,
} from 'sequelize-typescript';
import { MutationResolvers } from '../generated/graphql-types';
import { ApiContext } from '../main/context';
import { ResolversWithModels } from '../main/resolver-types';
import { ContestFile } from './contest-file';
import { ContestProblem } from './contest-problem';
import { FileContent } from './file-content';
import { Participation } from './participation';

export const contestSchema = gql`
    type Contest {
        name: ID!
        title: String!
        start: String!
        end: String!
        problems: [ContestProblem!]!
    }

    input ContestInput {
        name: ID!
        title: String!
        start: String!
        end: String!
    }
`;

/** A contest in TuringArena */
@Table
export class Contest extends Model<Contest> {
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

    /** The list of problems in this contest */
    @HasMany(() => ContestProblem)
    problems!: ContestProblem[];
    createProblem!: (
        problem: object,
        options?: object,
    ) => Promise<ContestProblem>;
    getProblems!: () => Promise<ContestProblem[]>;

    /** The list of users in this contest */
    @HasMany(() => Participation)
    participations!: Participation[];
    getParticipations!: (options: object) => Promise<Participation[]>;
    createParticipation!: (
        participation: object,
        options: object,
    ) => Promise<Participation>;
    addParticipation!: (options: object) => Promise<unknown>;

    /** The list of files in this contest */
    @HasMany(() => ContestFile)
    files!: ContestFile[];
    getFiles!: (options: object) => Promise<ContestFile[]>;
    createFile!: (
        contestFile: object,
        options?: object,
    ) => Promise<ContestFile>;

    /**
     * Add files to this contest
     *
     * @param ctx  Context of the database
     * @param base Base directory to add
     * @param dir  Relative directory in recursive call
     */
    async loadFiles(ctx: ApiContext, base: string, dir: string = '') {
        const files = fs.readdirSync(path.join(base, dir));
        for (const file of files) {
            const relPath = path.join(dir, file);
            if (fs.statSync(path.join(base, relPath)).isDirectory())
                await this.loadFiles(ctx, base, relPath);
            else {
                const fileRow = await FileContent.createFromPath(
                    ctx,
                    path.join(base, relPath),
                );
                await this.createFile({
                    path: relPath,
                    fileId: fileRow.id,
                });
            }
        }
    }
}

export const contestMutationResolvers: MutationResolvers = {
    addProblem: async ({}, { contestName, name }, ctx) => {
        const contest =
            (await ctx.db.Contest.findOne({
                where: { name: contestName },
            })) ?? ctx.fail(`no such contest '${contestName}'`);
        const problem =
            (await ctx.db.Problem.findOne({ where: { name } })) ??
            ctx.fail(`no such problem '${name}'`);
        await contest.createProblem({
            problem,
        });

        return true;
    },
    addUser: async ({}, { contestName, username }, ctx) => {
        const contest =
            (await ctx.db.Contest.findOne({
                where: { name: contestName },
            })) ?? ctx.fail(`no such contest '${contestName}'`);
        const user =
            (await ctx.db.User.findOne({ where: { username } })) ??
            ctx.fail(`no such user '${username}'`);
        await contest.addParticipation(user);

        return true;
    },
};

export const contestResolvers: ResolversWithModels<{
    Contest: Contest;
}> = {
    Contest: {
        start: contest => DateTime.fromJSDate(contest.start).toISO(),
        end: contest => DateTime.fromJSDate(contest.end).toISO(),
        problems: contest => contest.getProblems(),
    },
};
