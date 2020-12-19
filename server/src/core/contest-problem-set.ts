import { gql } from 'apollo-server-core';
import { ApiContext } from '../main/api-context';
import { Contest } from './contest';
import { ContestProblemSetUserTackling } from './contest-problem-set-user-tackling';
import { ScoreRange } from './feedback/score';

export const contestProblemSetSchema = gql`
    """
    Collection of problems in a contest.
    """
    type ContestProblemSet {
        """
        Contest containing this problem set.
        """
        contest: Contest!

        """
        Items in this problem set.
        Each corresponds to a problem assigned in the contest.
        """
        assignments: [ContestProblemAssignment!]!

        # TODO: grade domain
        userTacklings: [ContestProblemSetUserTackling!]!
    }
`;

export class ContestProblemSet {
    readonly ctx: ApiContext;
    constructor(readonly contest: Contest) {
        this.ctx = contest.ctx;
    }

    __typename = 'ContestProblemSet';

    async assignments() {
        return this.contest.getProblemAssignments();
    }

    async userTacklings(): Promise<ContestProblemSetUserTackling[]> {
        await this.ctx.authorizeAdmin();

        const users = await this.contest.getParticipatingUsers();
        return users.map(user => new ContestProblemSetUserTackling(this, user, this.ctx));
    }

    async getScoreRange(): Promise<ScoreRange> {
        const material = await this.contest.getProblemSetMaterial();

        return ScoreRange.total(material.map(m => m.scoreRange));
    }
}

export interface ContestProblemSetModelRecord {
    ContestProblemSet: ContestProblemSet;
}
