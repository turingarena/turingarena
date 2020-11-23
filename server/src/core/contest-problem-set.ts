import { gql } from 'apollo-server-core';
import { ApiContext } from '../main/api-context';
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

    __typename = 'ContestProblemSet';

    async assignments({}, ctx: ApiContext) {
        return this.contest.getProblemAssignments();
    }

    async getScoreRange(): Promise<ScoreRange> {
        const material = await this.contest.getProblemSetMaterial();

        return ScoreRange.total(material.map(m => m.scoreRange));
    }
}

export interface ContestProblemSetModelRecord {
    ContestProblemSet: ContestProblemSet;
}
