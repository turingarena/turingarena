import { gql } from 'apollo-server-core';
import { ApiContext } from '../main/api-context';
import { ApiOutputValue } from '../main/graphql-types';
import { ProblemDefinition } from './problem';

export const problemInstanceSchema = gql`
    type ProblemInstance {
        id: ID!

        contest: Contest!
        problem: ProblemDefinition!
    }
`;

export class ProblemInstance implements ApiOutputValue<'ProblemInstance'> {
    constructor(readonly problem: ProblemDefinition) {}

    __typename = 'ProblemInstance' as const;
    id() {
        return `${this.problem.contest.id}/${this.problem.name}`;
    }
    contest() {
        return this.problem.contest;
    }
    static fromId(id: string, ctx: ApiContext): ProblemInstance {
        return new ProblemInstance(ProblemDefinition.fromId(id, ctx));
    }
}
