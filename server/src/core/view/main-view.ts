import { gql } from 'apollo-server-core';
import { ApiContext } from '../../main/api-context';
import { Contest } from '../contest';
import { Text } from '../material/text';
import { SubmissionCache } from '../submission';
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
    constructor(readonly contest: Contest, readonly user: User | null, readonly ctx: ApiContext) {}
    async title() {
        return new Text([{ value: (await this.contest.getMetadata()).title ?? 'TuringArena' }]);
    }
    contestView() {
        return new ContestView(this.contest, this.user, this.ctx);
    }
    async pendingSubmissions() {
        return this.user !== null
            ? this.ctx.cache(SubmissionCache).pendingByContestAndUser.load({
                  contestId: this.contest.id,
                  username: this.user.username,
              })
            : [];
    }
}
