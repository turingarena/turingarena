import { gql } from 'apollo-server-core';
import { DateTime } from 'luxon';
import * as mime from 'mime-types';
import * as yaml from 'yaml';
import { ApiContext } from '../main/api-context';
import { ApiOutputValue } from '../main/graphql-types';
import { unreachable } from '../util/unreachable';
import { PackageTarget } from './archive/package-target';
import { ContestMetadata } from './contest-metadata';
import { ApiDateTime, DateTimeColumn, DateTimeField } from './data/date-time';
import { ApiTable, Column, Field, Record } from './data/field';
import { File, FileColumn, FileField } from './data/file';
import { HeaderColumn, HeaderField } from './data/header';
import { Media } from './data/media';
import { ScoreColumn, ScoreField } from './data/score';
import { Text } from './data/text';
import { FileContentService } from './files/file-content-service';
import { ProblemDefinition } from './problem-definition';
import { ProblemMaterial, ProblemMaterialCache } from './problem-definition-material';
import { ProblemInstance } from './problem-instance';
import { ProblemSetDefinition } from './problem-set-definition';
import { ProblemSetUndertaking } from './problem-set-undertaking';
import { ProblemUndertaking } from './problem-undertaking';
import { Submission, SubmissionCache } from './submission';
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

        userTable: Table!
        submissionTable: Table!
    }

    enum ContestStatus {
        NOT_STARTED
        RUNNING
        ENDED
    }
`;

export type ContestStatus = ApiOutputValue<'ContestStatus'>;

export class Contest implements ApiOutputValue<'Contest'> {
    constructor(readonly baseName: string, readonly ctx: ApiContext) {}

    __typename = 'Contest' as const;

    id = this.baseName;
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

        return new ProblemSetDefinition(this);
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
                    const content = (await archive.fileContent(path)) ?? unreachable();

                    this.ctx.service(FileContentService).publish(content);

                    return new File(
                        baseName,
                        null,
                        type !== false ? type : 'application/octet-stream',
                        content,
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
        // FIXME: is this needed?

        if (this.baseName !== 'default') unreachable(`cannot interact with non-default contest`);

        return this;
    }

    static getDefault(ctx: ApiContext) {
        return new Contest('default', ctx);
    }

    async getUserByName(name: string) {
        const contestMetadata = await this.getMetadata();
        const userMetadata = contestMetadata.users.find(data => data.username === name) ?? null;

        if (userMetadata === null) unreachable(`user not found`);

        return new User(this, userMetadata, this.ctx);
    }

    async getUserByToken(token: string) {
        const contestMetadata = await this.getMetadata();
        const userMetadata = contestMetadata.users.find(data => data.token === token) ?? null;

        if (userMetadata === null) return null;

        return new User(this, userMetadata, this.ctx);
    }

    async getParticipatingUsers() {
        const metadata = await this.getMetadata();

        return metadata.users.map(data => new User(this, data, this.ctx));
    }

    async userTable() {
        await this.ctx.authorizeAdmin();

        const contestMetadata = await this.getMetadata();
        const problemSet = await this.problemSet();
        const problems = await problemSet.problems();

        type MyColumn = [Column, (user: User) => Field | Promise<Field>];

        const columns: Array<MyColumn> = [
            [
                new HeaderColumn(new Text([{ value: 'ID' }])),
                user => new HeaderField(new Text([{ value: user.metadata.name }]), null),
            ],
            [
                new HeaderColumn(new Text([{ value: 'token' }])),
                user => new HeaderField(new Text([{ value: user.metadata.token }]), null),
            ],
            ...problems.map(
                (problem): MyColumn => [
                    new ScoreColumn(new Text([{ value: `Score ${problem.definition.baseName}` }])),
                    async user => {
                        const undertaking = new ProblemUndertaking(problem, user, user.ctx);
                        const { scoreRange, score } = await undertaking.totalScoreGrade();
                        return new ScoreField(scoreRange, score);
                    },
                ],
            ),
            [
                new ScoreColumn(new Text([{ value: 'Total score' }])),
                async user => {
                    const undertaking = new ProblemSetUndertaking(problemSet, user, user.ctx);
                    const { scoreRange, score } = await undertaking.totalScoreGrade();
                    return new ScoreField(scoreRange, score);
                },
            ],
        ];

        return new ApiTable(
            columns.map(([column]) => column),
            await Promise.all(
                contestMetadata.users.map(
                    async user =>
                        new Record(
                            await Promise.all(columns.map(([, mapper]) => mapper(new User(this, user, this.ctx)))),
                            null,
                        ),
                ),
            ),
        );
    }

    async submissionTable() {
        await this.ctx.authorizeAdmin();

        const problemSet = await this.problemSet();
        const problems = await problemSet.problems();

        const submissionFields = (
            await Promise.all(problems.map(problem => problem.definition.submissionFields()))
        ).flatMap(fields => fields);

        const submissionFieldNames = Array.from(new Set(submissionFields.map(field => field.name)));

        type MyColumn = [Column, (submission: Submission) => Field | Promise<Field>];

        const columns: Array<MyColumn> = [
            [
                new HeaderColumn(new Text([{ value: 'ID' }])),
                submission => new HeaderField(new Text([{ value: submission.id }]), null),
            ],
            [
                new HeaderColumn(new Text([{ value: 'Problem' }])),
                async submission =>
                    new HeaderField(new Text([{ value: (await submission.problem()).definition.baseName }]), null),
            ],
            [
                new HeaderColumn(new Text([{ value: 'User' }])),
                async submission =>
                    new HeaderField(new Text([{ value: (await submission.user()).metadata.name }]), null),
            ],
            [
                new DateTimeColumn(new Text([{ value: 'Time' }])),
                async submission => new DateTimeField(await submission.createdAt()),
            ],
            ...submissionFieldNames.map(
                (name): MyColumn => [
                    new FileColumn(new Text([{ value: name }])),
                    async submission => {
                        const items = await submission.items();
                        const item = items.find(item => item.field.name === name);
                        const file = item?.file ?? null;
                        if (file) this.ctx.service(FileContentService).publish(file.content);
                        return new FileField(file);
                    },
                ],
            ),
            [
                new ScoreColumn(new Text([{ value: 'Score' }])),
                async submission => {
                    const problem = await submission.problem();
                    const totalScoreDomain = await problem.definition.totalScoreDomain();
                    const totalScore = await submission.getTotalScore();
                    return new ScoreField(totalScoreDomain.scoreRange, totalScore?.score ?? null);
                },
            ],
        ];

        const submissions = await this.ctx.cache(SubmissionCache).byContest.load(this.id);

        return new ApiTable(
            columns.map(([column]) => column),
            await Promise.all(
                submissions.map(
                    async submission =>
                        new Record(await Promise.all(columns.map(([, mapper]) => mapper(submission))), null),
                ),
            ),
        );
    }
}
