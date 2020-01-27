import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../main/resolver-types';
import { Contest } from './contest';
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

    async getScoreRange(): Promise<ScoreRange> {
        return ScoreRange.total((await this.contest.getProblemSetMaterial()).map(m => m.scoreRange));
    }
}

export const contestProblemSetResolvers: ResolversWithModels<{
    ContestProblemSet: ContestProblemSet;
}> = {
    ContestProblemSet: {
        contest: ({ contest }) => contest,
        assignments: ({ contest }) => contest.getProblemAssignments(),
    },
};
