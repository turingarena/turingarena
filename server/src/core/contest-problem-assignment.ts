import { gql } from 'apollo-server-core';
import { ApiContext } from '../main/api-context';
import { ApiOutputValue } from '../main/graphql-types';
import { Problem } from './problem';

export const contestProblemAssignmentSchema = gql`
    type ContestProblemAssignment {
        id: ID!

        contest: Contest!
        problem: Problem!
    }
`;

export class ContestProblemAssignment implements ApiOutputValue<'ContestProblemAssignment'> {
    constructor(readonly problem: Problem) {}

    __typename = 'ContestProblemAssignment' as const;
    id() {
        return `${this.problem.contest.id}/${this.problem.name}`;
    }
    contest() {
        return this.problem.contest;
    }
    static fromId(id: string, ctx: ApiContext): ContestProblemAssignment {
        return new ContestProblemAssignment(Problem.fromId(id, ctx));
    }
}
