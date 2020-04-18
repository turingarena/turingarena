import { gql } from 'apollo-server-core';
import { Resolvers } from '../main/resolver-types';
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

export interface Problem {
    __typename: 'Problem';
    contest: Contest;
    name: string;
}

export interface ProblemModelRecord {
    Problem: Problem;
}

export const problemResolvers: Resolvers = {
    Problem: {
        id: p => `${p.contest.id}/${p.name}`,
        name: p => p.name,

        title: async (p, {}, ctx) => (await ctx.api(ProblemMaterialApi).dataLoader.load(p)).title,
        statement: async (p, {}, ctx) => (await ctx.api(ProblemMaterialApi).dataLoader.load(p)).statement,
        attachments: async (p, {}, ctx) => (await ctx.api(ProblemMaterialApi).dataLoader.load(p)).attachments,
        awards: async (p, {}, ctx) => (await ctx.api(ProblemMaterialApi).dataLoader.load(p)).awards,
        submissionFields: async (p, {}, ctx) => (await ctx.api(ProblemMaterialApi).dataLoader.load(p)).submissionFields,
        submissionFileTypes: async (p, {}, ctx) =>
            (await ctx.api(ProblemMaterialApi).dataLoader.load(p)).submissionFileTypes,
        submissionFileTypeRules: async (p, {}, ctx) =>
            (await ctx.api(ProblemMaterialApi).dataLoader.load(p)).submissionFileTypeRules,
        submissionListColumns: async (p, {}, ctx) =>
            (await ctx.api(ProblemMaterialApi).dataLoader.load(p)).submissionListColumns,
        evaluationFeedbackColumns: async (p, {}, ctx) =>
            (await ctx.api(ProblemMaterialApi).dataLoader.load(p)).evaluationFeedbackColumns,
        totalScoreDomain: async (p, {}, ctx) =>
            new ScoreGradeDomain((await ctx.api(ProblemMaterialApi).dataLoader.load(p)).scoreRange),
    },
};
