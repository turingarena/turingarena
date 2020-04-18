import { gql } from 'apollo-server-core';
import { Resolvers } from '../main/resolver-types';
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
    constructor(readonly contestId: string, readonly name: string) {}
}

export interface ProblemModelRecord {
    Problem: Problem;
}

export const problemResolvers: Resolvers = {
    Problem: {
        id: p => `${p.contestId}/${p.name}`,
        name: p => p.name,

        title: async (p, {}, ctx) =>
            (
                await ctx.api(ProblemMaterialApi).byContestAndProblemName.load({
                    contestId: p.contestId,
                    problemName: p.name,
                })
            ).title,
        statement: async (p, {}, ctx) =>
            (
                await ctx.api(ProblemMaterialApi).byContestAndProblemName.load({
                    contestId: p.contestId,
                    problemName: p.name,
                })
            ).statement,
        attachments: async (p, {}, ctx) =>
            (
                await ctx.api(ProblemMaterialApi).byContestAndProblemName.load({
                    contestId: p.contestId,
                    problemName: p.name,
                })
            ).attachments,
        awards: async (p, {}, ctx) =>
            (
                await ctx.api(ProblemMaterialApi).byContestAndProblemName.load({
                    contestId: p.contestId,
                    problemName: p.name,
                })
            ).awards,
        submissionFields: async (p, {}, ctx) =>
            (
                await ctx.api(ProblemMaterialApi).byContestAndProblemName.load({
                    contestId: p.contestId,
                    problemName: p.name,
                })
            ).submissionFields,
        submissionFileTypes: async (p, {}, ctx) =>
            (
                await ctx.api(ProblemMaterialApi).byContestAndProblemName.load({
                    contestId: p.contestId,
                    problemName: p.name,
                })
            ).submissionFileTypes,
        submissionFileTypeRules: async (p, {}, ctx) =>
            (
                await ctx.api(ProblemMaterialApi).byContestAndProblemName.load({
                    contestId: p.contestId,
                    problemName: p.name,
                })
            ).submissionFileTypeRules,
        submissionListColumns: async (p, {}, ctx) =>
            (
                await ctx.api(ProblemMaterialApi).byContestAndProblemName.load({
                    contestId: p.contestId,
                    problemName: p.name,
                })
            ).submissionListColumns,
        evaluationFeedbackColumns: async (p, {}, ctx) =>
            (
                await ctx.api(ProblemMaterialApi).byContestAndProblemName.load({
                    contestId: p.contestId,
                    problemName: p.name,
                })
            ).evaluationFeedbackColumns,
        totalScoreDomain: async (p, {}, ctx) =>
            new ScoreGradeDomain(
                (
                    await ctx.api(ProblemMaterialApi).byContestAndProblemName.load({
                        contestId: p.contestId,
                        problemName: p.name,
                    })
                ).scoreRange,
            ),
    },
};
