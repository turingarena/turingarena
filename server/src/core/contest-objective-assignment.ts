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
        problem: ProblemInstance!
        "The given objective."
        definition: ObjectiveDefinition!
    }
`;

export class ObjectiveInstance {
    constructor(readonly problem: ProblemInstance, readonly definition: ObjectiveDefinition) {}
    __typename = 'ObjectiveInstance' as const;
    id() {
        return `${this.problem.definition.contest.id}/${this.problem.definition.name}/${this.definition.index}`;
    }
}
