import { gql } from 'apollo-server-core';
import { ApiObject } from '../main/api';
import { ApiContext } from '../main/api-context';
import { Resolvers } from '../main/resolver-types';
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
    assignments({}, ctx: ApiContext) {
        return ctx.api(ContestApi).getProblemAssignments(this.contest);
    }
}

export interface ContestProblemSetModelRecord {
    ContestProblemSet: ContestProblemSet;
}

export class ContestProblemSetApi extends ApiObject {
    async getScoreRange(s: ContestProblemSet): Promise<ScoreRange> {
        const material = await this.ctx.api(ContestApi).getProblemSetMaterial(s.contest);

        return ScoreRange.total(material.map(m => m.scoreRange));
    }
}
