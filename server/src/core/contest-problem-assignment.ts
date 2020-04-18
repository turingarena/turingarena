import { gql } from 'apollo-server-core';
import { Resolvers } from '../main/resolver-types';
import { ContestApi } from './contest';
import { Problem } from './problem';

export const contestProblemAssignmentSchema = gql`
    type ContestProblemAssignment {
        id: ID!

        contest: Contest!
        problem: Problem!
    }
`;

export class ContestProblemAssignment {
    constructor(readonly contestId: string, readonly problemName: string) {}
}

export interface ContestProblemAssignmentModelRecord {
    ContestProblemAssignment: ContestProblemAssignment;
}

export const contestProblemAssignmentResolvers: Resolvers = {
    ContestProblemAssignment: {
        id: a => `${a.contestId}/${a.problemName}`,
        contest: (a, {}, ctx) => ctx.api(ContestApi).fromId(a.contestId),
        problem: (a, {}, ctx) => new Problem(a.contestId, a.problemName),
    },
};
