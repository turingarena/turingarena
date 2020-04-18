import { gql } from 'apollo-server-core';
import { DateTime } from 'luxon';
import * as mime from 'mime-types';
import { Op } from 'sequelize';
import { AllowNull, Column, DataType, ForeignKey, Table } from 'sequelize-typescript';
import * as yaml from 'yaml';
import { __generated_ContestStatus } from '../generated/graphql-types';
import { ApiObject } from '../main/api';
import { createByIdLoader, createSimpleLoader, UuidBaseModel } from '../main/base-model';
import { Resolvers } from '../main/resolver-types';
import { ContestMetadata } from './contest-metadata';
import { ContestProblemAssignment } from './contest-problem-assignment';
import { ContestProblemSet } from './contest-problem-set';
import { Archive } from './files/archive';
import { FileContent } from './files/file-content';
import { Media, MediaVariant } from './material/media';
import { ProblemMaterial, ProblemMaterialApi } from './material/problem-material';
import { User } from './user';

export const contestSchema = gql`
    type Contest {
        id: ID!
        name: String!
        title: Text!

        "Statement of this contest, presented as its home page"
        statement: Media!

        start: DateTime!
        end: DateTime!

        status: ContestStatus!
        problemSet: ContestProblemSet!
        archive: Archive!
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
    @AllowNull(false)
    @Column(DataType.UUIDV4)
    @ForeignKey(() => Archive)
    archiveId!: string;
}

export type ContestStatus = __generated_ContestStatus;

export interface MutationModelRecord {
    Mutation: {};
}

export interface ContestModelRecord {
    Contest: Contest;
}

export class ContestApi extends ApiObject {
    byId = createByIdLoader(this.ctx, Contest);
    byName = createSimpleLoader(async (name: string) => {
        // FIXME: should contests be addressable by name anyway?

        const contests = await this.ctx.table(Contest).findAll();
        const metadata = await Promise.all(contests.map(async c => this.getMetadata(c)));

        return contests.find((c, i) => metadata[i].name === name) ?? null;
    });

    async getDefault() {
        // FIXME: assumes there is only one contest
        return this.ctx.table(Contest).findOne();
    }

    async getMetadata(c: Contest) {
        const metadataPath = `turingarena.yaml`;
        const metadataProblemFile = await this.ctx.table(Archive).findOne({
            where: {
                uuid: c.archiveId,
                path: metadataPath,
            },
        });

        if (metadataProblemFile === null) {
            throw new Error(`Contest ${c.id} is missing metadata file ${metadataPath}`);
        }

        const metadataContent = await this.ctx
            .table(FileContent)
            .findOne({ where: { id: metadataProblemFile.contentId } });

        return yaml.parse(metadataContent!.content.toString()) as ContestMetadata;
    }

    async getUserByUsername(c: Contest, username: string) {
        const metadata = await this.ctx.api(ContestApi).getMetadata(c);
        const userMetadata = metadata.users.find(u => u.username === username) ?? null;

        if (userMetadata === null) throw new Error(`contest ${c.id} has no user '${username}'`);

        return new User(c.id, userMetadata);
    }

    async getUserByToken(c: Contest, token: string) {
        const metadata = await this.ctx.api(ContestApi).getMetadata(c);
        const userMetadata = metadata.users.find(u => u.token === token) ?? null;

        if (userMetadata === null) return null;

        return new User(c.id, userMetadata);
    }

    async getStatus(c: Contest): Promise<ContestStatus> {
        const metadata = await this.getMetadata(c);

        const start = DateTime.fromISO(metadata.start).valueOf();
        const end = DateTime.fromISO(metadata.end).valueOf();
        const now = DateTime.local().valueOf();

        if (now < start) return 'NOT_STARTED';
        else if (now < end) return 'RUNNING';
        else return 'NOT_STARTED';
    }

    async getProblemAssignments(c: Contest) {
        const metadata = await this.getMetadata(c);

        return metadata.problems.map(name => new ContestProblemAssignment(c.id, name));
    }

    async getProblemSetMaterial(c: Contest): Promise<ProblemMaterial[]> {
        const assignments = await this.getProblemAssignments(c);

        return Promise.all(
            assignments.map(async ({ contestId, problemName }) =>
                this.ctx.api(ProblemMaterialApi).byContestAndProblemName.load({
                    contestId,
                    problemName,
                }),
            ),
        );
    }

    private statementVariantFromFile(archiveFile: Archive): MediaVariant {
        const type = mime.lookup(archiveFile.path);
        const pathParts = archiveFile.path.split('/');

        return {
            name: pathParts[pathParts.length - 1],
            type: type !== false ? type : 'application/octet-stream',
            content: () => archiveFile.getContent(),
        };
    }

    async getStatement(c: Contest): Promise<Media> {
        const statementFiles = await this.ctx.table(Archive).findAll({
            where: {
                uuid: c.archiveId,
                path: {
                    [Op.like]: 'files/home%',
                },
            },
        });

        return statementFiles.map((archiveFile): MediaVariant => this.statementVariantFromFile(archiveFile));
    }
}

export const contestResolvers: Resolvers = {
    Contest: {
        id: c => c.id,
        name: async (c, {}, ctx) => (await ctx.api(ContestApi).getMetadata(c)).name,
        title: async (c, {}, ctx) => [{ value: (await ctx.api(ContestApi).getMetadata(c)).title }],
        start: async (c, {}, ctx) => (await ctx.api(ContestApi).getMetadata(c)).start,
        end: async (c, {}, ctx) => (await ctx.api(ContestApi).getMetadata(c)).end,
        status: (c, {}, ctx) => ctx.api(ContestApi).getStatus(c),
        problemSet: c => new ContestProblemSet(c),
        archive: c => ({ uuid: c.archiveId }),
        statement: (c, {}, ctx) => ctx.api(ContestApi).getStatement(c),
    },
};
