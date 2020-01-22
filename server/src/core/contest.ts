import { gql } from 'apollo-server-core';
import * as fs from 'fs';
import { DateTime } from 'luxon';
import * as path from 'path';
import { AllowNull, Column, HasMany, Index, Table, Unique } from 'sequelize-typescript';
import { ContestStatus, MutationResolvers } from '../generated/graphql-types';
import { BaseModel } from '../main/base-model';
import { ApiContext } from '../main/context';
import { ResolversWithModels } from '../main/resolver-types';
import { ContestFile } from './contest-file';
import { ContestProblemAssignment } from './contest-problem-assignment';
import { FileContent } from './file-content';
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

    /** The list of files in this contest */
    @HasMany(() => ContestFile)
    files!: ContestFile[];
    getFiles!: (options: object) => Promise<ContestFile[]>;
    createFile!: (contestFile: object, options?: object) => Promise<ContestFile>;

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
            if (fs.statSync(path.join(base, relPath)).isDirectory()) await this.loadFiles(ctx, base, relPath);
            else {
                const fileRow = await FileContent.createFromPath(ctx, path.join(base, relPath));
                await this.createFile({
                    path: relPath,
                    fileId: fileRow.id,
                });
            }
        }
    }

    getStatus(): ContestStatus {
        const start = DateTime.fromJSDate(this.start).valueOf();
        const end = DateTime.fromJSDate(this.end).valueOf();
        const now = DateTime.local().valueOf();

        if (now < start) return 'NOT_STARTED';
        else if (now < end) return 'RUNNING';
        else return 'NOT_STARTED';
    }
}

export const contestMutationResolvers: MutationResolvers = {
    addProblem: async ({}, { contestName, name }, ctx) => {
        const contest =
            (await ctx.table(Contest).findOne({
                where: { name: contestName },
            })) ?? ctx.fail(`no such contest '${contestName}'`);
        const problem =
            (await ctx.table(Problem).findOne({ where: { name } })) ?? ctx.fail(`no such problem '${name}'`);
        await contest.createProblemAssignment({
            problem,
        });

        return true;
    },
    addUser: async ({}, { contestName, username }, ctx) => {
        const contest =
            (await ctx.table(Contest).findOne({
                where: { name: contestName },
            })) ?? ctx.fail(`no such contest '${contestName}'`);
        const user = (await ctx.table(User).findOne({ where: { username } })) ?? ctx.fail(`no such user '${username}'`);
        await contest.addParticipation(user);

        return true;
    },
};

export const contestResolvers: ResolversWithModels<{
    Contest: Contest;
}> = {
    Contest: {
        title: contest => [{ value: contest.title }],
        start: contest => DateTime.fromJSDate(contest.start).toISO(),
        end: contest => DateTime.fromJSDate(contest.end).toISO(),
        status: contest => contest.getStatus(),
        problemSet: contest => contest,
    },
};
