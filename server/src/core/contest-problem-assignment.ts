import { gql } from 'apollo-server-core';
import { Problem } from './problem';

export const contestProblemAssignmentSchema = gql`
    type ContestProblemAssignment {
        id: ID!

        contest: Contest!
        problem: Problem!
    }
`;

export class ContestProblemAssignment {
    constructor(readonly problem: Problem) {}
    __typename = 'ContestProblemAssignment';
    id() {
        return `${this.problem.contest.id}/${this.problem.name}`;
    }
    contest() {
        return this.problem.contest;
    }
}

export interface ContestProblemAssignmentModelRecord {
    ContestProblemAssignment: ContestProblemAssignment;
}
