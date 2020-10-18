import { gql } from 'apollo-server-core';
import { DateTime } from 'luxon';
import * as mime from 'mime-types';
import { Op } from 'sequelize';
import { AllowNull, Column, DataType, ForeignKey, Table } from 'sequelize-typescript';
import * as yaml from 'yaml';
import { __generated_ContestStatus } from '../generated/graphql-types';
import { ApiObject } from '../main/api';
import { createSimpleLoader, UuidBaseModel } from '../main/base-model';
import { Resolvers } from '../main/resolver-types';
import { typed } from '../util/types';
import { ContestMetadata } from './contest-metadata';
import { ContestProblemAssignment } from './contest-problem-assignment';
import { Archive } from './files/archive';
import { FileContent } from './files/file-content';
import { Media, MediaVariant } from './material/media';
import { ProblemMaterial, ProblemMaterialApi } from './material/problem-material';

export const contestSchema = gql`
    type Contest {
        id: ID!
        name: String!
        title: Text!

        "Statement of this contest, presented as its home page"
        statement: Media!

        start: DateTime!
        end: DateTime

        status: ContestStatus!
        problemSet: ContestProblemSet!
        archive: Archive!
    }

    enum ContestStatus {
        NOT_STARTED
        RUNNING
        ENDED
    }
`;

/** A contest in TuringArena */
@Table
export class ContestData extends UuidBaseModel<ContestData> {
    @AllowNull(false)
    @Column(DataType.UUIDV4)
    @ForeignKey(() => Archive)
    archiveId!: string;
}

export interface Contest {
    __typename: 'Contest';
    id: string;
}

export type ContestStatus = __generated_ContestStatus;

export interface MutationModelRecord {
    Mutation: {};
}

export interface ContestModelRecord {
    Contest: Contest;
}

export class ContestApi extends ApiObject {
    fromId(id: string): Contest {
        return { __typename: 'Contest', id };
    }

    fromData(data: ContestData): Contest {
        return this.fromId(data.id);
    }

    dataLoader = createSimpleLoader(({ id }: Contest) => this.ctx.table(ContestData).findByPk(id));

    async validate(contest: Contest) {
        await this.dataLoader.load(contest);

        return contest;
    }

    byNameLoader = createSimpleLoader(async (name: string) => {
        // FIXME: should contests be addressable by name anyway?

        const contests = await this.ctx.table(ContestData).findAll();
        const metadata = await Promise.all(contests.map(d => this.fromData(d)).map(async c => this.getMetadata(c)));

        return contests.find((c, i) => metadata[i].name === name) ?? null;
    });

    async getDefault(): Promise<Contest | null> {
        // FIXME: assumes there is only one contest
        const data = await this.ctx.table(ContestData).findOne();
        if (data === null) return null;

        return {
            __typename: 'Contest',
            id: data.id,
        };
    }

    async getMetadata(c: Contest) {
        const { archiveId } = await this.dataLoader.load(c);
        const metadataPath = `turingarena.yaml`;
        const metadataProblemFile = await this.ctx.table(Archive).findOne({
            where: {
                uuid: archiveId,
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

    async getStatus(c: Contest): Promise<ContestStatus> {
        const metadata = await this.getMetadata(c);

        const start = DateTime.fromISO(metadata.start).valueOf();
        const end = metadata.end !== undefined ? DateTime.fromISO(metadata.end).valueOf() : null;
        const now = DateTime.local().valueOf();

        if (now < start) return 'NOT_STARTED';
        else if (end === null || now < end) return 'RUNNING';
        else return 'ENDED';
    }

    async getProblemAssignments(contest: Contest) {
        const metadata = await this.getMetadata(contest);

        return metadata.problems.map(name =>
            typed<ContestProblemAssignment>({
                __typename: 'ContestProblemAssignment',
                problem: { __typename: 'Problem', contest, name },
            }),
        );
    }

    async getProblemSetMaterial(c: Contest): Promise<ProblemMaterial[]> {
        const assignments = await this.getProblemAssignments(c);

        return Promise.all(
            assignments.map(async ({ problem }) => this.ctx.api(ProblemMaterialApi).dataLoader.load(problem)),
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
        const { archiveId } = await this.dataLoader.load(c);
        const statementFiles = await this.ctx.table(Archive).findAll({
            where: {
                uuid: archiveId,
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
        end: async (c, {}, ctx) => (await ctx.api(ContestApi).getMetadata(c)).end ?? null,
        status: (c, {}, ctx) => ctx.api(ContestApi).getStatus(c),
        problemSet: c => ({ __typename: 'ContestProblemSet', contest: c }),
        archive: async (c, {}, ctx) => {
            await ctx.authorizeAdmin();

            return { uuid: (await ctx.api(ContestApi).dataLoader.load(c)).archiveId };
        },
        statement: (c, {}, ctx) => ctx.api(ContestApi).getStatement(c),
    },
};
