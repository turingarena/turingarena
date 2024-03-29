import { gql } from 'apollo-server-core';
import { ApiContext } from '../main/api-context';
import { Contest } from './contest';
import { ProblemSetDefinition } from './problem-set-definition';
import { ProblemSetView } from './problem-set-view';
import { User } from './user';
import { ApiOutputValue } from '../main/graphql-types';

export const contestViewSchema = gql`
    """
    A given contest, as seen by a given user or anonymously.
    """
    type ContestView {
        "The given contest."
        contest: Contest!
        "The given user."
        user: User

        "The problem-set of the given contest, as seen by the same user, if it is currently visible, and null otherwise."
        problemSet: ProblemSetView
    }
`;

export class ContestView implements ApiOutputValue<'ContestView'> {
    constructor(readonly contest: Contest, readonly user: User | null, readonly ctx: ApiContext) {}

    __typename = 'ContestView' as const;

    async problemSet() {
        const status = await this.contest.getStatus();
        switch (status) {
            case 'RUNNING':
            case 'ENDED':
                return new ProblemSetView(new ProblemSetDefinition(this.contest), this.user, this.ctx);
            case 'NOT_STARTED':
            default:
                return null;
        }
    }
}
