import { gql } from 'apollo-server-core';
import { DateTime } from 'luxon';
import * as mime from 'mime-types';
import { Op } from 'sequelize';
import { AllowNull, Column, DataType, ForeignKey, Table } from 'sequelize-typescript';
import * as yaml from 'yaml';
import { ApiCache } from '../main/api-cache';
import { ApiContext } from '../main/api-context';
import { createSimpleLoader, UuidBaseModel } from '../main/base-model';
import { ApiOutputValue } from '../main/graphql-types';
import { ContestMetadata } from './contest-metadata';
import { ProblemInstance } from './contest-problem-assignment';
import { ProblemSetDefinition } from './contest-problem-set';
import { Archive, ArchiveFileData } from './files/archive';
import { FileContent } from './files/file-content';
import { Media, MediaFile } from './material/media';
import { ProblemMaterial, ProblemMaterialCache } from './material/problem-material';
import { Text } from './material/text';
import { ProblemDefinition } from './problem';
import { User } from './user';
import { ApiDateTime } from './util/date-time';

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
        problemSet: ProblemSetDefinition!
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
    @ForeignKey(() => ArchiveFileData)
    archiveId!: string;

    getContest(ctx: ApiContext) {
        return new Contest(this.id, ctx);
    }
}

export type ContestStatus = ApiOutputValue<'ContestStatus'>;

export class Contest implements ApiOutputValue<'Contest'> {
    constructor(readonly id: string, readonly ctx: ApiContext) {}

    __typename = 'Contest' as const;
    async name() {
        return (await this.getMetadata()).name;
    }
    async title() {
        return new Text([{ value: (await this.getMetadata()).title }]);
    }
    async start() {
        const start = (await this.getMetadata()).start;

        return ApiDateTime.fromISO(start);
    }
    async end() {
        const end = (await this.getMetadata()).end;

        return end === undefined ? null : ApiDateTime.fromISO(end);
    }
    async status() {
        return this.getStatus();
    }
    async problemSet() {
        await this.ctx.authorizeAdmin();

        return (new ProblemSetDefinition(this) as unknown) as ApiOutputValue<'ProblemSetDefinition'>;
    }
    async archive() {
        await this.ctx.authorizeAdmin();

        return new Archive((await this.ctx.cache(ContestCache).byId.load(this.id)).archiveId, this.ctx);
    }
    async statement() {
        const { archiveId } = await this.ctx.cache(ContestCache).byId.load(this.id);
        const statementFiles = await this.ctx.table(ArchiveFileData).findAll({
            where: {
                uuid: archiveId,
                path: {
                    [Op.like]: 'files/home%',
                },
            },
        });

        return new Media(statementFiles.map((archiveFile): MediaFile => this.getStatementVariantFromFile(archiveFile)));
    }

    async getMetadata() {
        const { archiveId } = await this.ctx.cache(ContestCache).byId.load(this.id);
        const metadataPath = `turingarena.yaml`;
        const metadataProblemFile = await this.ctx.table(ArchiveFileData).findOne({
            where: {
                uuid: archiveId,
                path: metadataPath,
            },
        });

        if (metadataProblemFile === null) {
            throw new Error(`Contest ${this.id} is missing metadata file ${metadataPath}`);
        }

        const metadataContent = await this.ctx
            .table(FileContent)
            .findOne({ where: { id: metadataProblemFile.contentId } });

        return yaml.parse(metadataContent!.content.toString()) as ContestMetadata;
    }

    async getStatus(): Promise<ContestStatus> {
        const metadata = await this.getMetadata();

        const start = DateTime.fromISO(metadata.start).valueOf();
        const end = metadata.end !== undefined ? DateTime.fromISO(metadata.end).valueOf() : null;
        const now = DateTime.local().valueOf();

        if (now < start) return 'NOT_STARTED';
        else if (end === null || now < end) return 'RUNNING';
        else return 'ENDED';
    }

    async getProblems() {
        const metadata = await this.getMetadata();

        return metadata.problems.map(name => new ProblemInstance(new ProblemDefinition(this, name, this.ctx)));
    }

    async getProblemSetMaterial(): Promise<ProblemMaterial[]> {
        const problems = await this.getProblems();

        return Promise.all(
            problems.map(async ({ definition }) => this.ctx.cache(ProblemMaterialCache).byId.load(definition.id())),
        );
    }

    async validate() {
        await this.ctx.cache(ContestCache).byId.load(this.id);

        return this;
    }

    static async getDefault(ctx: ApiContext): Promise<Contest | null> {
        // FIXME: assumes there is only one contest
        const data = await ctx.table(ContestData).findOne();
        if (data === null) return null;

        return data.getContest(ctx);
    }

    async getUserByToken(token: string) {
        const contestMetadata = await this.getMetadata();
        const userMetadata = contestMetadata.users.find(data => data.token === token) ?? null;

        if (userMetadata === null) return null;
        const { username } = userMetadata;

        return new User(this, username, this.ctx);
    }

    async getParticipatingUsers() {
        const metadata = await this.getMetadata();

        return metadata.users.map(data => new User(this, data.username, this.ctx));
    }

    getStatementVariantFromFile(archiveFile: ArchiveFileData): MediaFile {
        const type = mime.lookup(archiveFile.path);
        const pathParts = archiveFile.path.split('/');

        return new MediaFile(
            pathParts[pathParts.length - 1],
            null,
            type !== false ? type : 'application/octet-stream',
            archiveFile.getContent(),
            this.ctx,
        );
    }
}

export class ContestCache extends ApiCache {
    byId = createSimpleLoader((id: string) => this.ctx.table(ContestData).findByPk(id));
    byName = createSimpleLoader(async (name: string) => {
        // FIXME: should contests be addressable by name anyway?

        const contests = await this.ctx.table(ContestData).findAll();
        const metadata = await Promise.all(contests.map(d => d.getContest(this.ctx)).map(async c => c.getMetadata()));

        return contests.find((c, i) => metadata[i].name === name) ?? null;
    });
}
