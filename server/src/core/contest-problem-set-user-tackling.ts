import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../main/resolver-types';
import { ContestProblemAssignmentUserTackling } from './contest-problem-assignment-user-tackling';
import { ContestProblemSet } from './contest-problem-set';
import { ContestProblemSetView } from './contest-problem-set-view';
import { ScoreGrade } from './feedback/score';
import { User } from './user';

export const contestProblemSetUserTacklingSchema = gql`
    """
    The problem set of a given contest, tackled by a given user.
    """
    type ContestProblemSetUserTackling {
        "The problem set."
        problemSet: ContestProblemSet!
        "The given user."
        user: User!

        "Same problem-set seen by same user."
        view: ContestProblemSetView!
    }
`;

export class ContestProblemSetUserTackling {
    constructor(readonly problemSet: ContestProblemSet, readonly user: User) {}

    async getScoreGrade() {
        return ScoreGrade.total(
            await Promise.all(
                (await this.problemSet.contest.getProblemAssignments()).map(async a =>
                    new ContestProblemAssignmentUserTackling(a, this.user).getScoreGrade(),
                ),
            ),
        );
    }
}

export const contestAssignmentUserTacklingResolvers: ResolversWithModels<{
    ContestProblemSetUserTackling: ContestProblemSetUserTackling;
}> = {
    ContestProblemSetUserTackling: {
        problemSet: ({ problemSet }) => problemSet,
        user: ({ user }) => user,
        view: ({ problemSet, user }) => new ContestProblemSetView(problemSet, user),
    },
};
