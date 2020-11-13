import { gql } from 'apollo-server-core';
import { ApiContext } from '../main/api-context';
import { Contest, ContestApi } from './contest';
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
        assignments: [ContestProblemAssignment]!

        # TODO: grade domain
    }
`;

export class ContestProblemSet {
    constructor(readonly contest: Contest) {}

    __typename = 'ContestProblemSet';

    async assignments({}, ctx: ApiContext) {
        return ctx.api(ContestApi).getProblemAssignments(this.contest);
    }

    async getScoreRange(ctx: ApiContext): Promise<ScoreRange> {
        const material = await ctx.api(ContestApi).getProblemSetMaterial(this.contest);

        return ScoreRange.total(material.map(m => m.scoreRange));
    }
}

export interface ContestProblemSetModelRecord {
    ContestProblemSet: ContestProblemSet;
}
