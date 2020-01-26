import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../main/resolver-types';
import { Contest } from './contest';
import { ContestProblemUserTackling } from './contest-problem-user-tackling';
import { ContestView } from './contest-view';
import { ScoreValue } from './feedback/score';
import { User } from './user';

export const contestUserTacklingSchema = gql`
    """
    A given contest, tackled by a given user.
    """
    type ContestUserTackling {
        "The given contest."
        contest: Contest!
        "The given user."
        user: User!

        "The problem-set of the given contest, as seen by the given user."
        problemSetView: ContestProblemSetView!
    }
`;

export class ContestUserTackling {
    constructor(readonly contest: Contest, readonly user: User) {}

    async getScore() {
        return ScoreValue.total(
            await Promise.all(
                (await this.contest.getProblemAssignments()).map(async a =>
                    new ContestProblemUserTackling(a, this.user).getScore(),
                ),
            ),
        );
    }
}

export const contestUserTacklingResolvers: ResolversWithModels<{
    ContestUserTackling: ContestUserTackling;
}> = {
    ContestUserTackling: {
        contest: ({ contest }) => contest,
        user: ({ user }) => user,
        problemSetView: ({ contest, user }) => new ContestView(contest, user),
    },
};
