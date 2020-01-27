import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../main/resolver-types';
import { Contest } from './contest';
import { ContestProblemAssignmentUserTackling } from './contest-problem-assignment-user-tackling';
import { ContestView } from './contest-view';
import { ScoreValue } from './feedback/score';
import { User } from './user';

export const contestProblemSetUserTacklingSchema = gql`
    """
    The problem set of a given contest, tackled by a given user.
    """
    type ContestProblemSetUserTackling {
        "The given contest."
        contest: Contest!
        "The given user."
        user: User!

        "Same problem-set seen by same user."
        view: ContestProblemSetView!
    }
`;

export class ContestProblemSetUserTackling {
    constructor(readonly contest: Contest, readonly user: User) {}

    async getScore() {
        return ScoreValue.total(
            await Promise.all(
                (await this.contest.getProblemAssignments()).map(async a =>
                    new ContestProblemAssignmentUserTackling(a, this.user).getScore(),
                ),
            ),
        );
    }
}

export const contestAssignmentUserTacklingResolvers: ResolversWithModels<{
    ContestProblemSetUserTackling: ContestProblemSetUserTackling;
}> = {
    ContestProblemSetUserTackling: {
        contest: ({ contest }) => contest,
        user: ({ user }) => user,
        view: ({ contest, user }) => new ContestView(contest, user),
    },
};
