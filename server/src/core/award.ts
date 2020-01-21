import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../main/resolver-types';
import { Problem } from './problem';

export const awardSchema = gql`
    """
    Graded element in a problem.
    For every award of a problem, a progressively higher grade can be achieved during a contest.
    Corresponds to a subtask in IOI-like problems, assuming max-by-subtask scoring.
    """
    type Award {
        problem: Problem!
    }
`;

export class Award {
    constructor(readonly problem: Problem, readonly index: number) {}
}

export const awardResolvers: ResolversWithModels<{
    Award: Award;
}> = {
    Award: {
        // TODO: id: ({ problem, index }) => `${problem.id}/${index}`,
        problem: ({ problem }) => problem,
    },
};
