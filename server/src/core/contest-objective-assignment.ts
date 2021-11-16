import { gql } from 'apollo-server-core';
import { ProblemInstance } from './contest-problem-assignment';
import { ObjectiveDefinition } from './material/objective';

export const objectiveInstanceSchema = gql`
    """
    Revers to a given objective of a problem, assigned in a given contest.
    """
    type ObjectiveInstance {
        id: ID!

        "The problem containing the given objective, assigned in the same contest."
        problemAssignment: ProblemInstance!
        "The given objective."
        objective: ObjectiveDefinition!
    }
`;

export class ObjectiveInstance {
    constructor(readonly problemAssignment: ProblemInstance, readonly objective: ObjectiveDefinition) {}
    __typename = 'ObjectiveInstance' as const;
    id() {
        return `${this.problemAssignment.problem.contest.id}/${this.problemAssignment.problem.name}/${this.objective.index}`;
    }
}
