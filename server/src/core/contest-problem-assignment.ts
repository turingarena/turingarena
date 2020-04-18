import { gql } from 'apollo-server-core';
import { Resolvers } from '../main/resolver-types';
import { Problem } from './problem';

export const contestProblemAssignmentSchema = gql`
    type ContestProblemAssignment {
        id: ID!

        contest: Contest!
        problem: Problem!
    }
`;

export interface ContestProblemAssignment {
    __typename: 'ContestProblemAssignment';
    problem: Problem;
}

export interface ContestProblemAssignmentModelRecord {
    ContestProblemAssignment: ContestProblemAssignment;
}

export const contestProblemAssignmentResolvers: Resolvers = {
    ContestProblemAssignment: {
        id: a => `${a.problem.contest.id}/${a.problem.name}`,
        contest: (a, {}, ctx) => a.problem.contest,
        problem: (a, {}, ctx) => a.problem,
    },
};
