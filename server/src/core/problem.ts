import { gql } from 'apollo-server-core';
import { ApiContext } from '../main/api-context';
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

export class Problem {
    constructor(readonly contest: Contest, readonly name: string) {}
    __typename = 'Problem';

    static fromId(id: string, ctx: ApiContext): Problem {
        const [contestId, problemName] = id.split('/');

        return new Problem(new Contest(contestId, ctx), problemName);
    }

    id() {
        return `${this.contest.id}/${this.name}`;
    }
    async title({}, ctx: ApiContext) {
        return (await ctx.api(ProblemMaterialApi).dataLoader.load(this.id())).title;
    }
    async statement({}, ctx: ApiContext) {
        return (await ctx.api(ProblemMaterialApi).dataLoader.load(this.id())).statement;
    }
    async attachments({}, ctx: ApiContext) {
        return (await ctx.api(ProblemMaterialApi).dataLoader.load(this.id())).attachments;
    }
    async attributes({}, ctx: ApiContext) {
        return (await ctx.api(ProblemMaterialApi).dataLoader.load(this.id())).attributes;
    }
    async awards({}, ctx: ApiContext) {
        return (await ctx.api(ProblemMaterialApi).dataLoader.load(this.id())).awards;
    }
    async submissionFields({}, ctx: ApiContext) {
        return (await ctx.api(ProblemMaterialApi).dataLoader.load(this.id())).submissionFields;
    }
    async submissionFileTypes({}, ctx: ApiContext) {
        return (await ctx.api(ProblemMaterialApi).dataLoader.load(this.id())).submissionFileTypes;
    }
    async submissionFileTypeRules({}, ctx: ApiContext) {
        return (await ctx.api(ProblemMaterialApi).dataLoader.load(this.id())).submissionFileTypeRules;
    }
    async submissionListColumns({}, ctx: ApiContext) {
        return (await ctx.api(ProblemMaterialApi).dataLoader.load(this.id())).submissionListColumns;
    }
    async evaluationFeedbackColumns({}, ctx: ApiContext) {
        return (await ctx.api(ProblemMaterialApi).dataLoader.load(this.id())).evaluationFeedbackColumns;
    }
    async totalScoreDomain({}, ctx: ApiContext) {
        return new ScoreGradeDomain((await ctx.api(ProblemMaterialApi).dataLoader.load(this.id())).scoreRange);
    }
}

export interface ProblemModelRecord {
    Problem: Problem;
}
