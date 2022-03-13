import { gql } from 'apollo-server-core';
import { ApiContext } from '../main/api-context';
import { ApiOutputValue } from '../main/graphql-types';
import { ProblemDefinition } from './problem-definition';

export const problemInstanceSchema = gql`
    type ProblemInstance {
        id: ID!

        contest: Contest!
        definition: ProblemDefinition!
    }
`;

export class ProblemInstance implements ApiOutputValue<'ProblemInstance'> {
    constructor(readonly definition: ProblemDefinition) {}

    __typename = 'ProblemInstance' as const;

    id = `${this.definition.contest.id}/${this.definition.baseName}`;

    contest() {
        return this.definition.contest;
    }

    static fromId(id: string, ctx: ApiContext): ProblemInstance {
        return new ProblemInstance(ProblemDefinition.fromId(id, ctx));
    }
}
