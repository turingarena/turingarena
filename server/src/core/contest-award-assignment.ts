import { gql } from 'apollo-server-core';
import { Resolvers } from '../main/resolver-types';
import { ContestProblemAssignment } from './contest-problem-assignment';
import { Award } from './material/award';

export const contestAwardAssignmentSchema = gql`
    """
    Revers to a given award of a problem, assigned in a given contest.
    """
    type ContestAwardAssignment {
        "The problem containing the given award, assigned in the same contest."
        problemAssignment: ContestProblemAssignment!
        "The given award."
        award: Award!
    }
`;

export class ContestAwardAssignment {
    constructor(readonly problemAssignment: ContestProblemAssignment, readonly award: Award) {}
}

export interface ContestAwardAssignmentModelRecord {
    ContestAwardAssignment: ContestAwardAssignment;
}

export const contestAwardAssignmentResolvers: Resolvers = {
    ContestAwardAssignment: {
        problemAssignment: assignment => assignment.problemAssignment,
        award: assignment => assignment.award,
    },
};
