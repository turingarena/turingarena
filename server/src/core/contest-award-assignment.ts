import { gql } from 'apollo-server-core';
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

export class ContestAwardAssignment {
    constructor(readonly problemAssignment: ContestProblemAssignment, readonly award: Award) {}
    __typename = 'ContestAwardAssignment' as const;
    id() {
        return `${this.problemAssignment.problem.contest.id}/${this.problemAssignment.problem.name}/${this.award.index}`;
    }
}

export interface ContestAwardAssignmentModelRecord {
    ContestAwardAssignment: ContestAwardAssignment;
}
