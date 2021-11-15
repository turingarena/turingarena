import { gql } from 'apollo-server-core';
import { ContestProblemAssignment } from './contest-problem-assignment';
import { Objective } from './material/objective';

export const contestObjectiveAssignmentSchema = gql`
    """
    Revers to a given objective of a problem, assigned in a given contest.
    """
    type ContestObjectiveAssignment {
        id: ID!

        "The problem containing the given objective, assigned in the same contest."
        problemAssignment: ContestProblemAssignment!
        "The given objective."
        objective: Objective!
    }
`;

export class ContestObjectiveAssignment {
    constructor(readonly problemAssignment: ContestProblemAssignment, readonly objective: Objective) {}
    __typename = 'ContestObjectiveAssignment' as const;
    id() {
        return `${this.problemAssignment.problem.contest.id}/${this.problemAssignment.problem.name}/${this.objective.index}`;
    }
}
