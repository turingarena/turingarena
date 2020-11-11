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
    id() {
        return `${this.contest.id}/${this.name}`;
    }
    async title({}, ctx: ApiContext) {
        return (await ctx.api(ProblemMaterialApi).dataLoader.load(this)).title;
    }
    async statement({}, ctx: ApiContext) {
        return (await ctx.api(ProblemMaterialApi).dataLoader.load(this)).statement;
    }
    async attachments({}, ctx: ApiContext) {
        return (await ctx.api(ProblemMaterialApi).dataLoader.load(this)).attachments;
    }
    async attributes({}, ctx: ApiContext) {
        return (await ctx.api(ProblemMaterialApi).dataLoader.load(this)).attributes;
    }
    async awards({}, ctx: ApiContext) {
        return (await ctx.api(ProblemMaterialApi).dataLoader.load(this)).awards;
    }
    async submissionFields({}, ctx: ApiContext) {
        return (await ctx.api(ProblemMaterialApi).dataLoader.load(this)).submissionFields;
    }
    async submissionFileTypes({}, ctx: ApiContext) {
        return (await ctx.api(ProblemMaterialApi).dataLoader.load(this)).submissionFileTypes;
    }
    async submissionFileTypeRules({}, ctx: ApiContext) {
        return (await ctx.api(ProblemMaterialApi).dataLoader.load(this)).submissionFileTypeRules;
    }
    async submissionListColumns({}, ctx: ApiContext) {
        return (await ctx.api(ProblemMaterialApi).dataLoader.load(this)).submissionListColumns;
    }
    async evaluationFeedbackColumns({}, ctx: ApiContext) {
        (await ctx.api(ProblemMaterialApi).dataLoader.load(this)).evaluationFeedbackColumns;
    }
    async totalScoreDomain({}, ctx: ApiContext) {
        new ScoreGradeDomain((await ctx.api(ProblemMaterialApi).dataLoader.load(this)).scoreRange);
    }
}

export interface ProblemModelRecord {
    Problem: Problem;
}