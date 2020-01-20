import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../main/resolver-types';
import { Contest } from './contest';

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
        items: [ContestProblemSetItem]!

        # TODO: grade domain
    }
`;

export const contestProblemSetResolvers: ResolversWithModels<{
    ContestProblemSet: Contest;
}> = {
    ContestProblemSet: {
        contest: contest => contest,
        items: contest => contest.getProblemSetItems(),
    },
};
