import { gql } from 'apollo-server-core';
import { ApiContext } from '../../main/api-context';
import { Contest } from '../contest';
import { ContestProblemSet } from '../contest-problem-set';
import { User } from '../user';
import { ContestProblemSetView } from './contest-problem-set-view';

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
        problemSetView: ContestProblemSetView
    }
`;

export class ContestView {
    constructor(readonly contest: Contest, readonly user: User | null, readonly ctx: ApiContext) {}
    __typename = 'ContestView' as const;
    async problemSetView() {
        const status = await this.contest.getStatus();
        switch (status) {
            case 'RUNNING':
            case 'ENDED':
                return new ContestProblemSetView(new ContestProblemSet(this.contest), this.user, this.ctx);
            case 'NOT_STARTED':
            default:
                return null;
        }
    }
}
