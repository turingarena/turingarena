import { gql } from 'apollo-server-core';
import { DateTime } from 'luxon';
import * as mime from 'mime-types';
import { Op } from 'sequelize';
import { AllowNull, Column, DataType, ForeignKey, Table } from 'sequelize-typescript';
import * as yaml from 'yaml';
import { __generated_ContestStatus } from '../generated/graphql-types';
import { ApiObject } from '../main/api';
import { ApiContext } from '../main/api-context';
import { createSimpleLoader, UuidBaseModel } from '../main/base-model';
import { ContestMetadata } from './contest-metadata';
import { ContestProblemAssignment } from './contest-problem-assignment';
import { ContestProblemSet } from './contest-problem-set';
import { Archive } from './files/archive';
import { FileContent } from './files/file-content';
import { Media, MediaFile } from './material/media';
import { ProblemMaterial, ProblemMaterialApi } from './material/problem-material';
import { Problem } from './problem';
import { User } from './user';

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

    getContest(ctx: ApiContext) {
        return new Contest(this.id, ctx);
    }
}

export type ContestStatus = __generated_ContestStatus;

export interface MutationModelRecord {
    Mutation: {};
}

export interface ContestModelRecord {
    Contest: Contest;
}

export class ContestApi extends ApiObject {
    dataLoader = createSimpleLoader((id: string) => this.ctx.table(ContestData).findByPk(id));

    byNameLoader = createSimpleLoader(async (name: string) => {
        // FIXME: should contests be addressable by name anyway?

        const contests = await this.ctx.table(ContestData).findAll();
        const metadata = await Promise.all(
            contests.map(d => d.getContest(this.ctx)).map(async c => c.getMetadata()),
        );

        return contests.find((c, i) => metadata[i].name === name) ?? null;
    });

    private statementVariantFromFile(archiveFile: Archive): MediaFile {
        const type = mime.lookup(archiveFile.path);
        const pathParts = archiveFile.path.split('/');

        return new MediaFile(
            pathParts[pathParts.length - 1],
            null,
            type !== false ? type : 'application/octet-stream',
            () => archiveFile.getContent(),
        );
    }

    async getStatement(c: Contest): Promise<Media> {
        const { archiveId } = await this.dataLoader.load(c.id);
        const statementFiles = await this.ctx.table(Archive).findAll({
            where: {
                uuid: archiveId,
                path: {
                    [Op.like]: 'files/home%',
                },
            },
        });

        return statementFiles.map((archiveFile): MediaFile => this.statementVariantFromFile(archiveFile));
    }

}

export class Contest {
    constructor(readonly id: string, readonly ctx: ApiContext) {}

    __typename = 'Contest';
    async name() {
        return (await this.getMetadata()).name;
    }
    async title() {
        return [{ value: (await this.getMetadata()).title }];
    }
    async start() {
        return (await this.getMetadata()).start;
    }
    async end() {
        return (await this.getMetadata()).end ?? null;
    }
    async status() {
        return this.getStatus();
    }
    problemSet() {
        return new ContestProblemSet(this);
    }
    async archive() {
        await this.ctx.authorizeAdmin();

        return { uuid: (await this.ctx.api(ContestApi).dataLoader.load(this.id)).archiveId };
    }
    async statement() {
        return this.ctx.api(ContestApi).getStatement(this);
    }

    async getMetadata() {
        const { archiveId } = await this.ctx.api(ContestApi).dataLoader.load(this.id);
        const metadataPath = `turingarena.yaml`;
        const metadataProblemFile = await this.ctx.table(Archive).findOne({
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

    async getProblemAssignments() {
        const metadata = await this.getMetadata();

        return metadata.problems.map(name => new ContestProblemAssignment(new Problem(this, name)));
    }

    async getProblemSetMaterial(): Promise<ProblemMaterial[]> {
        const assignments = await this.getProblemAssignments();

        return Promise.all(
            assignments.map(async ({ problem }) => this.ctx.api(ProblemMaterialApi).dataLoader.load(problem.id())),
        );
    }

    async validate() {
        await this.ctx.api(ContestApi).dataLoader.load(this.id);

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

        return new User(this, username);
    }
}
