import { gql } from 'apollo-server-core';
import { ApiContext } from '../main/api-context';
import { ApiOutputValue } from '../main/graphql-types';
import { unreachable } from '../util/unreachable';
import { PackageTarget } from './archive/package-target';
import { Contest } from './contest';
import { ScoreGradeDomain } from './data/score';
import { ProblemMaterialCache } from './problem-definition-material';

export const problemSchema = gql`
    type ProblemDefinition {
        id: ID!
        baseName: String!
        fullName: String!
        package: PackageTarget!
    }

    input ProblemInput {
        name: ID!
        files: [ID!]!
    }
`;

export class ProblemDefinition implements ApiOutputValue<'ProblemDefinition'> {
    constructor(readonly contest: Contest, readonly baseName: string) {}

    __typename = 'ProblemDefinition' as const;

    ctx = this.contest.ctx;
    fullName = `${this.contest.fullName}/problems/${this.baseName}`;
    id = `${this.contest.id}/${this.baseName}`;

    static fromId(id: string, ctx: ApiContext): ProblemDefinition {
        const [contestId, problemName] = id.split('/');

        return new ProblemDefinition(new Contest(contestId, ctx), problemName);
    }

    async package() {
        await this.ctx.authorizeAdmin();

        return this.packageUnchecked();
    }

    async packageUnchecked() {
        const contestLocation = await this.contest.packageUnchecked.mainLocation();

        return new PackageTarget(this.ctx, this.fullName, `${contestLocation.path}/problems/${this.baseName}`);
    }

    async archiveUnchecked() {
        const problemPackage = await this.packageUnchecked();
        const revision = await problemPackage.mainRevision();
        const archive = revision?.archive() ?? null;

        if (archive === null) throw unreachable(`problem has no archive`);

        return archive;
    }

    async title() {
        return (await this.ctx.cache(ProblemMaterialCache).byId.load(this.id)).title;
    }

    async statement() {
        return (await this.ctx.cache(ProblemMaterialCache).byId.load(this.id)).statement();
    }

    async attachments() {
        return (await this.ctx.cache(ProblemMaterialCache).byId.load(this.id)).attachments();
    }

    async attributes() {
        return (await this.ctx.cache(ProblemMaterialCache).byId.load(this.id)).attributes;
    }

    async objectives() {
        return (await this.ctx.cache(ProblemMaterialCache).byId.load(this.id)).objectives;
    }

    async submissionFields() {
        return (await this.ctx.cache(ProblemMaterialCache).byId.load(this.id)).submissionFields;
    }

    async submissionFileTypes() {
        return (await this.ctx.cache(ProblemMaterialCache).byId.load(this.id)).submissionFileTypes;
    }

    async submissionFileTypeRules() {
        return (await this.ctx.cache(ProblemMaterialCache).byId.load(this.id)).submissionFileTypeRules;
    }

    async submissionListColumns() {
        return (await this.ctx.cache(ProblemMaterialCache).byId.load(this.id)).submissionListColumns;
    }

    async evaluationFeedbackColumns() {
        return (await this.ctx.cache(ProblemMaterialCache).byId.load(this.id)).evaluationFeedbackColumns;
    }

    async totalScoreDomain() {
        return new ScoreGradeDomain((await this.ctx.cache(ProblemMaterialCache).byId.load(this.id)).scoreRange);
    }
}
