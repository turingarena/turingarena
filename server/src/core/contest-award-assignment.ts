import { gql } from 'apollo-server-core';
import { Resolvers } from '../main/resolver-types';
import { ContestProblemAssignment } from './contest-problem-assignment';
import { Award } from './material/award';

export const contestAwardAssignmentSchema = gql`
    """
    Revers to a given award of a problem, assigned in a given contest.
    """
    type ContestAwardAssignment {
        id: ID!

        "The problem containing the given award, assigned in the same contest."
        problemAssignment: ContestProblemAssignment!
        "The given award."
        award: Award!
    }
`;

export interface ContestAwardAssignment {
    __typename: 'ContestAwardAssignment';
    problemAssignment: ContestProblemAssignment;
    award: Award;
}

export interface ContestAwardAssignmentModelRecord {
    ContestAwardAssignment: ContestAwardAssignment;
}

export const contestAwardAssignmentResolvers: Resolvers = {
    ContestAwardAssignment: {
        id: a => `${a.problemAssignment.problem.contest.id}/${a.problemAssignment.problem.name}/${a.award.index}`,
        problemAssignment: a => a.problemAssignment,
        award: a => a.award,
    },
};
