import { gql } from 'apollo-server-core';
import { ObjectiveDefinition } from './objective-definition';
import { ProblemInstance } from './problem-instance';
import { ApiOutputValue } from '../main/graphql-types';

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

export class ObjectiveInstance implements ApiOutputValue<'ObjectiveInstance'> {
    constructor(readonly problem: ProblemInstance, readonly definition: ObjectiveDefinition) {}
    __typename = 'ObjectiveInstance' as const;
    id = `${this.problem.definition.contest.id}/${this.problem.definition.baseName}/${this.definition.index}`
}
