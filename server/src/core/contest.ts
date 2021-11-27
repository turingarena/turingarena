import { gql } from 'apollo-server-core';
import { DateTime } from 'luxon';
import * as mime from 'mime-types';
import { AllowNull, Column, DataType, ForeignKey, Table } from 'sequelize-typescript';
import * as yaml from 'yaml';
import { ApiCache } from '../main/api-cache';
import { ApiContext } from '../main/api-context';
import { createSimpleLoader, UuidBaseModel } from '../main/base-model';
import { ApiOutputValue } from '../main/graphql-types';
import { unreachable } from '../util/unreachable';
import { PackageTarget } from './archive/package-target';
import { ContestMetadata } from './contest-metadata';
import { ApiDateTime } from './data/date-time';
import { File } from './data/file';
import { Media } from './data/media';
import { Text } from './data/text';
import { ArchiveFileData } from './files/archive';
import { ProblemDefinition } from './problem-definition';
import { ProblemMaterial, ProblemMaterialCache } from './problem-definition-material';
import { ProblemInstance } from './problem-instance';
import { ProblemSetDefinition } from './problem-set-definition';
import { User } from './user';

export const contestSchema = gql`
    type Contest {
        id: ID!

        fullName: String!
        baseName: String!

        title: Text!

        "Statement of this contest, presented as its home page"
        statement: Media!

        start: DateTime!
        end: DateTime

        status: ContestStatus!
        problemSet: ProblemSetDefinition!

        package: PackageTarget!
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

    baseName = this.id;
    fullName = `contests/${this.baseName}`;

    packageUnchecked = new PackageTarget(this.ctx, this.fullName, this.fullName);

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

    async package() {
        await this.ctx.authorizeAdmin();

        return this.packageUnchecked;
    }

    async statement() {
        const archive = await this.getArchive();

        const lsOutput = await archive.execInDir(`ls files/home.*`);
        const filePaths = lsOutput.split('\n');
        filePaths.pop(); // FIXME: re-use this logic

        return new Media(
            await Promise.all(
                filePaths.map(async path => {
                    const type = mime.lookup(path);
                    const pathParts = path.split('/');
                    const baseName = pathParts[pathParts.length - 1];
                    const content = await archive.fileContent(path);

                    return new File(
                        baseName,
                        null,
                        type !== false ? type : 'application/octet-stream',
                        content ?? unreachable(),
                        this.ctx,
                    );
                }),
            ),
        );
    }

    async getMetadata() {
        const archive = await this.getArchive();
        const metadataYaml = await archive.fileContent(`turingarena.yaml`);
        if (metadataYaml === null) throw unreachable(`contest is missing metadata file`); // FIXME

        return yaml.parse(metadataYaml.utf8()) as ContestMetadata;
    }

    async getArchive() {
        const revision = await this.packageUnchecked.mainRevision();
        const archive = revision?.archive() ?? null;
        if (archive === null) throw unreachable(`contest has no archive`); // FIXME

        return archive;
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

        return metadata.problems.map(name => new ProblemInstance(new ProblemDefinition(this, name)));
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
        const data = await ctx.table(ContestData).findOne({ where: { id: 'default' } });
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
}

export class ContestCache extends ApiCache {
    byId = createSimpleLoader((id: string) => this.ctx.table(ContestData).findByPk(id));
}
