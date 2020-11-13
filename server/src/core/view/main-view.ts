import { gql } from 'apollo-server-core';
import { ApiContext } from '../../main/api-context';
import { Contest } from '../contest';
import { SubmissionApi } from '../submission';
import { User } from '../user';
import { ContestView } from './contest-view';

export const mainViewSchema = gql`
    """
    Data visible in a front page, i.e., to contestants, as seen by a given user or anonymously.
    """
    type MainView {
        "The given user, if any, or null if anonymous."
        user: User

        "The title of the page."
        title: Text!

        "The contest to show by default, or null if there is no default contest."
        contestView: ContestView

        """
        Relevant submissions that are currently pending.
        Used to poll data for such submissions more frequently, when the list is non-empty.
        """
        pendingSubmissions: [Submission!]!
    }
`;

export class MainView {
    constructor(readonly contest: Contest, readonly user: User | null) {}
    async title({}, ctx: ApiContext) {
        return [{ value: (await this.contest.getMetadata(ctx)).title ?? 'TuringArena' }];
    }
    contestView() {
        return new ContestView(this.contest, this.user);
    }
    async pendingSubmissions({}, ctx: ApiContext) {
        return this.user !== null
            ? ctx.api(SubmissionApi).pendingByContestAndUser.load({
                  contestId: this.contest.id,
                  username: this.user.username,
              })
            : [];
    }
}

export interface MainViewModelRecord {
    MainView: MainView;
}
