import { gql } from 'apollo-server-core';
import { ApiContext } from '../main/api-context';
import { ApiOutputValue } from '../main/graphql-types';
import { Contest } from './contest';
import { ScoreGradeDomain } from './feedback/score';
import { ProblemMaterialApi } from './material/problem-material';

export const problemSchema = gql`
    type Problem {
        id: ID!
        name: ID!
    }

    input ProblemInput {
        name: ID!
        files: [ID!]!
    }
`;

export class Problem implements ApiOutputValue<'Problem'> {
    constructor(readonly contest: Contest, readonly name: string, readonly ctx: ApiContext) {}
    __typename = 'Problem' as const;

    static fromId(id: string, ctx: ApiContext): Problem {
        const [contestId, problemName] = id.split('/');

        return new Problem(new Contest(contestId, ctx), problemName, ctx);
    }

    id() {
        return `${this.contest.id}/${this.name}`;
    }
    async title() {
        return (await this.ctx.cache(ProblemMaterialApi).dataLoader.load(this.id())).title;
    }
    async statement() {
        return (await this.ctx.cache(ProblemMaterialApi).dataLoader.load(this.id())).statement;
    }
    async attachments() {
        return (await this.ctx.cache(ProblemMaterialApi).dataLoader.load(this.id())).attachments;
    }
    async attributes() {
        return (await this.ctx.cache(ProblemMaterialApi).dataLoader.load(this.id())).attributes;
    }
    async awards() {
        return (await this.ctx.cache(ProblemMaterialApi).dataLoader.load(this.id())).awards;
    }
    async submissionFields() {
        return (await this.ctx.cache(ProblemMaterialApi).dataLoader.load(this.id())).submissionFields;
    }
    async submissionFileTypes() {
        return (await this.ctx.cache(ProblemMaterialApi).dataLoader.load(this.id())).submissionFileTypes;
    }
    async submissionFileTypeRules() {
        return (await this.ctx.cache(ProblemMaterialApi).dataLoader.load(this.id())).submissionFileTypeRules;
    }
    async submissionListColumns() {
        return (await this.ctx.cache(ProblemMaterialApi).dataLoader.load(this.id())).submissionListColumns;
    }
    async evaluationFeedbackColumns() {
        return (await this.ctx.cache(ProblemMaterialApi).dataLoader.load(this.id())).evaluationFeedbackColumns;
    }
    async totalScoreDomain() {
        return new ScoreGradeDomain((await this.ctx.cache(ProblemMaterialApi).dataLoader.load(this.id())).scoreRange);
    }
}
