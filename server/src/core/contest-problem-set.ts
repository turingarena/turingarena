import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../main/resolver-types';
import { Contest } from './contest';
import { ScoreDomain } from './feedback/score';

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

    async getScoreDomain(): Promise<ScoreDomain> {
        return ScoreDomain.total((await this.contest.getProblemSetMaterial()).map(m => m.scoreDomain));
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
