import { gql } from 'apollo-server-core';
import { ApiContext } from '../main/api-context';
import { ApiOutputValue } from '../main/graphql-types';
import { Contest } from './contest';
import { ScoreGradeDomain } from './data/score';
import { ProblemMaterialCache } from './problem-definition-material';

export const problemSchema = gql`
    type ProblemDefinition {
        id: ID!
        name: ID!
    }

    input ProblemInput {
        name: ID!
        files: [ID!]!
    }
`;

export class ProblemDefinition implements ApiOutputValue<'ProblemDefinition'> {
    constructor(readonly contest: Contest, readonly name: string, readonly ctx: ApiContext) {}
    __typename = 'ProblemDefinition' as const;

    static fromId(id: string, ctx: ApiContext): ProblemDefinition {
        const [contestId, problemName] = id.split('/');

        return new ProblemDefinition(new Contest(contestId, ctx), problemName, ctx);
    }

    id() {
        return `${this.contest.id}/${this.name}`;
    }
    async title() {
        return (await this.ctx.cache(ProblemMaterialCache).byId.load(this.id())).title;
    }
    async statement() {
        return (await this.ctx.cache(ProblemMaterialCache).byId.load(this.id())).statement();
    }
    async attachments() {
        return (await this.ctx.cache(ProblemMaterialCache).byId.load(this.id())).attachments();
    }
    async attributes() {
        return (await this.ctx.cache(ProblemMaterialCache).byId.load(this.id())).attributes;
    }
    async objectives() {
        return (await this.ctx.cache(ProblemMaterialCache).byId.load(this.id())).objectives;
    }
    async submissionFields() {
        return (await this.ctx.cache(ProblemMaterialCache).byId.load(this.id())).submissionFields;
    }
    async submissionFileTypes() {
        return (await this.ctx.cache(ProblemMaterialCache).byId.load(this.id())).submissionFileTypes;
    }
    async submissionFileTypeRules() {
        return (await this.ctx.cache(ProblemMaterialCache).byId.load(this.id())).submissionFileTypeRules;
    }
    async submissionListColumns() {
        return (await this.ctx.cache(ProblemMaterialCache).byId.load(this.id())).submissionListColumns;
    }
    async evaluationFeedbackColumns() {
        return (await this.ctx.cache(ProblemMaterialCache).byId.load(this.id())).evaluationFeedbackColumns;
    }
    async totalScoreDomain() {
        return new ScoreGradeDomain((await this.ctx.cache(ProblemMaterialCache).byId.load(this.id())).scoreRange);
    }
}
