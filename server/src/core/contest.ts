import { gql } from 'apollo-server-core';
import { DateTime } from 'luxon';
import * as mime from 'mime-types';
import * as yaml from 'yaml';
import { ApiContext } from '../main/api-context';
import { ApiOutputValue } from '../main/graphql-types';
import { unreachable } from '../util/unreachable';
import { PackageRevision } from './archive/package-revision';
import { PackageTarget } from './archive/package-target';
import { ContestMetadata } from './contest-metadata';
import { ApiDateTime, DateTimeColumn, DateTimeField } from './data/date-time';
import {
    ApiTable,
    AtomicColumnDefinition,
    ColumnDefinition,
    GroupColumnDefinition,
    mapTable,
    TableDefinition,
} from './data/field';
import { File, FileColumn, FileField } from './data/file';
import { FulfillmentColumn, FulfillmentField } from './data/fulfillment';
import { HeaderColumn, HeaderField } from './data/header';
import { Media } from './data/media';
import { ScoreColumn, ScoreField, ScoreGradeDomain } from './data/score';
import { Text } from './data/text';
import { Evaluation, EvaluationCache } from './evaluation';
import { FileContentService } from './files/file-content-service';
import { ObjectiveDefinition } from './objective-definition';
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

        contestTable: Table!
        problemTable: Table!
        userTable: Table!
        submissionTable: Table!
        evaluationTable: Table!
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

    revisionTableDefinition: TableDefinition<PackageRevision> = [
        new AtomicColumnDefinition(
            i => new HeaderColumn(new Text([{ value: 'Path' }]), i),
            async revision =>
                revision.archiveHash === null
                    ? null
                    : new HeaderField(new Text([{ value: revision.branch.location.path }]), null),
        ),
        new AtomicColumnDefinition(
            i => new HeaderColumn(new Text([{ value: 'Branch name' }]), i),
            async revision =>
                revision.archiveHash === null
                    ? null
                    : new HeaderField(new Text([{ value: revision.branch.name }]), null),
        ),
        new AtomicColumnDefinition(
            i => new HeaderColumn(new Text([{ value: 'Commit hash' }]), i),
            async revision =>
                revision.archiveHash === null
                    ? null
                    : new HeaderField(new Text([{ value: revision.commitHash }]), null),
        ),
        new AtomicColumnDefinition(
            i => new HeaderColumn(new Text([{ value: 'Archive hash' }]), i),
            async revision =>
                revision.archiveHash === null
                    ? null
                    : new HeaderField(new Text([{ value: revision.archiveHash }]), null),
        ),
    ];

    packageTableDefinition: TableDefinition<PackageTarget> = [
        ...mapTable<PackageTarget, PackageRevision>(this.revisionTableDefinition, async target =>
            target.mainRevision(),
        ),
    ];

    async contestTable() {
        await this.ctx.authorizeAdmin();

        const columns: TableDefinition<this> = [
            new AtomicColumnDefinition(
                i => new HeaderColumn(new Text([{ value: 'ID' }]), i),
                problem => new HeaderField(new Text([{ value: problem.id }]), null),
            ),
            ...mapTable<this, PackageTarget>(this.packageTableDefinition, async contest => contest.packageUnchecked),
        ];

        return ApiTable.fromColumnDefinitions(columns, [this]);
    }

    async problemTable() {
        await this.ctx.authorizeAdmin();

        const problemSet = await this.problemSet();
        const problems = await problemSet.problems();

        const columns: TableDefinition<ProblemInstance> = [
            new AtomicColumnDefinition(
                i => new HeaderColumn(new Text([{ value: 'ID' }]), i),
                problem => new HeaderField(new Text([{ value: problem.id }]), null),
            ),
            ...mapTable<ProblemInstance, PackageTarget>(this.packageTableDefinition, async problem =>
                problem.definition.packageUnchecked(),
            ),
        ];

        return ApiTable.fromColumnDefinitions(columns, problems);
    }

    async userTable() {
        await this.ctx.authorizeAdmin();

        const contestMetadata = await this.getMetadata();
        const problemSet = await this.problemSet();
        const problems = await problemSet.problems();

        const columns: TableDefinition<User> = [
            new AtomicColumnDefinition(
                i => new HeaderColumn(new Text([{ value: 'ID' }]), i),
                user => new HeaderField(new Text([{ value: user.metadata.name }]), null),
            ),
            new AtomicColumnDefinition(
                i => new HeaderColumn(new Text([{ value: 'token' }]), i),
                user => new HeaderField(new Text([{ value: user.metadata.token }]), null),
            ),
            ...problems.map(
                (problem): ColumnDefinition<User> =>
                    new AtomicColumnDefinition(
                        i => new ScoreColumn(new Text([{ value: `Score ${problem.definition.baseName}` }]), i),
                        async user => {
                            const undertaking = new ProblemUndertaking(problem, user, user.ctx);
                            const { scoreRange, score } = await undertaking.totalScoreGrade();
                            return new ScoreField(scoreRange, score);
                        },
                    ),
            ),
            new AtomicColumnDefinition(
                i => new ScoreColumn(new Text([{ value: 'Total score' }]), i),
                async user => {
                    const undertaking = new ProblemSetUndertaking(problemSet, user, user.ctx);
                    const { scoreRange, score } = await undertaking.totalScoreGrade();
                    return new ScoreField(scoreRange, score);
                },
            ),
        ];

        const users = contestMetadata.users.map(metadata => new User(this, metadata, this.ctx));
        return ApiTable.fromColumnDefinitions(columns, users);
    }

    async submissionTable() {
        await this.ctx.authorizeAdmin();

        const columns: TableDefinition<Submission> = await this.submissionTableGenerator();
        const submissions = await this.ctx.cache(SubmissionCache).byContest.load(this.id);

        return ApiTable.fromColumnDefinitions(columns, submissions);
    }

    private async submissionTableGenerator(): Promise<TableDefinition<Submission>> {
        const problemSet = await this.problemSet();
        const problems = await problemSet.problems();

        const submissionFields = (
            await Promise.all(problems.map(problem => problem.definition.submissionFields()))
        ).flatMap(fields => fields);

        const submissionFieldNames = Array.from(new Set(submissionFields.map(field => field.name)));

        return [
            new AtomicColumnDefinition(
                i => new HeaderColumn(new Text([{ value: 'ID' }]), i),
                submission => new HeaderField(new Text([{ value: submission.id }]), null),
            ),
            new AtomicColumnDefinition(
                i => new HeaderColumn(new Text([{ value: 'Problem' }]), i),
                async submission =>
                    new HeaderField(new Text([{ value: (await submission.problem()).definition.baseName }]), null),
            ),
            new AtomicColumnDefinition(
                i => new HeaderColumn(new Text([{ value: 'User' }]), i),
                async submission =>
                    new HeaderField(new Text([{ value: (await submission.user()).metadata.name }]), null),
            ),
            new AtomicColumnDefinition(
                i => new DateTimeColumn(new Text([{ value: 'Time' }]), i),
                async submission => new DateTimeField(await submission.createdAt()),
            ),
            ...submissionFieldNames.map(
                (name): ColumnDefinition<Submission> =>
                    new AtomicColumnDefinition(
                        i => new FileColumn(new Text([{ value: name }]), i),
                        async submission => {
                            const items = await submission.items();
                            const item = items.find(item => item.field.name === name);
                            const file = item?.file ?? null;
                            if (file) this.ctx.service(FileContentService).publish(file.content);
                            return new FileField(file);
                        },
                    ),
            ),
            ...mapTable<Submission, Evaluation>(await this.evaluationInfoTableDefinition(), async submission =>
                submission.officialEvaluation(),
            ),
        ];
    }

    async evaluationTable() {
        await this.ctx.authorizeAdmin();

        return ApiTable.fromColumnDefinitions(
            await this.evaluationTableDefinition(),
            (await this.ctx.cache(EvaluationCache).all.load('')).map(data => new Evaluation(data.id, this.ctx)),
        );
    }

    private async evaluationTableDefinition(): Promise<TableDefinition<Evaluation>> {
        return [
            new AtomicColumnDefinition(
                i => new HeaderColumn(new Text([{ value: 'ID' }]), i),
                evaluation => new HeaderField(new Text([{ value: evaluation.id }]), null),
            ),
            new AtomicColumnDefinition(
                i => new HeaderColumn(new Text([{ value: 'Submission' }]), i),
                async evaluation => new HeaderField(new Text([{ value: (await evaluation.submission()).id }]), null),
            ),
            new AtomicColumnDefinition(
                i => new HeaderColumn(new Text([{ value: 'Problem Name' }]), i),
                async evaluation =>
                    new HeaderField(
                        new Text([{ value: (await (await evaluation.submission()).problem()).definition.baseName }]),
                        null,
                    ),
            ),
            ...(await this.evaluationInfoTableDefinition()),
        ];
    }

    private async evaluationInfoTableDefinition(): Promise<TableDefinition<Evaluation>> {
        return [
            new AtomicColumnDefinition(
                i => new HeaderColumn(new Text([{ value: 'Problem Archive Hash' }]), i),
                async evaluation => new HeaderField(new Text([{ value: await evaluation.problemArchiveHash() }]), null),
            ),
            new AtomicColumnDefinition(
                i => new DateTimeColumn(new Text([{ value: 'Time' }]), i),
                async evaluation => new DateTimeField(ApiDateTime.fromJSDate((await evaluation.getData()).createdAt)),
            ),
            new GroupColumnDefinition(new Text([{ value: 'Outcome' }]), [
                {
                    show: 'ALWAYS',
                    column: new AtomicColumnDefinition(
                        i => new ScoreColumn(new Text([{ value: 'Total score' }]), i),
                        async evaluation => {
                            const { score, scoreRange } = await evaluation.getTotalScore();
                            return new ScoreField(scoreRange, score);
                        },
                    ),
                },
                ...(await this.evaluationObjectiveTableDefinition()).map(column => ({
                    show: 'WHEN_OPEN' as const,
                    column,
                })),
            ]),
        ];
    }

    private async evaluationObjectiveTableDefinition() {
        const problemSet = await this.problemSet();
        const problems = await problemSet.problems();

        const problemObjectives = await Promise.all(
            problems.map(async problem => ({ problem, objectives: await problem.definition.objectives() })),
        );

        return problemObjectives.map(
            ({ problem, objectives }) =>
                new GroupColumnDefinition(new Text([{ value: problem.definition.baseName }]), [
                    {
                        show: 'ALWAYS',
                        column: new AtomicColumnDefinition<Evaluation>(
                            i => new ScoreColumn(new Text([{ value: 'Total score' }]), i),
                            async evaluation => {
                                const submissionProblem = await (await evaluation.submission()).problem();
                                if (submissionProblem.id !== problem.id) return null;
                                const { score, scoreRange } = await evaluation.getTotalScore();
                                return new ScoreField(scoreRange, score);
                            },
                        ),
                    },
                    ...objectives.map(objective => ({
                        show: 'WHEN_OPEN' as const,
                        column: getObjectiveColumnDefinition(objective),
                    })),
                ]),
        );
    }
}

function getObjectiveColumnDefinition(objective: ObjectiveDefinition) {
    const gradeDomain = objective.gradeDomain;
    return gradeDomain instanceof ScoreGradeDomain
        ? new AtomicColumnDefinition<Evaluation>(
              i => new ScoreColumn(objective.title, i),
              async evaluation => {
                  const outcome = await evaluation.getOutcome(objective);
                  if (!outcome) return null;
                  return new ScoreField(gradeDomain.scoreRange, outcome?.grade ?? null);
              },
          )
        : new AtomicColumnDefinition<Evaluation>(
              i => new FulfillmentColumn(objective.title, i),
              async evaluation => {
                  const outcome = await evaluation.getOutcome(objective);
                  if (!outcome) return null;
                  const fulfilled = outcome === null ? null : outcome.grade > 0;
                  return new FulfillmentField(fulfilled);
              },
          );
}
