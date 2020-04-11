import { gql } from 'apollo-server-core';
import { ApiObject } from '../main/api';
import { Resolvers } from '../main/resolver-types';
import { ContestProblemAssignmentApi } from './contest-problem-assignment';
import {
    ContestProblemAssignmentUserTackling,
    ContestProblemAssignmentUserTacklingApi,
} from './contest-problem-assignment-user-tackling';
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
}

export interface ContestProblemSetUserTacklingModelRecord {
    ContestProblemSetUserTackling: ContestProblemSetUserTackling;
}

export class ContestProblemSetUserTacklingApi extends ApiObject {
    async getScoreGrade(t: ContestProblemSetUserTackling) {
        const assignments = await this.ctx
            .api(ContestProblemAssignmentApi)
            .allByContestId.load(t.problemSet.contest.id);

        return ScoreGrade.total(
            await Promise.all(
                assignments.map(async a =>
                    this.ctx
                        .api(ContestProblemAssignmentUserTacklingApi)
                        .getScoreGrade(new ContestProblemAssignmentUserTackling(a, t.user)),
                ),
            ),
        );
    }
}

export const contestAssignmentUserTacklingResolvers: Resolvers = {
    ContestProblemSetUserTackling: {
        problemSet: ({ problemSet }) => problemSet,
        user: ({ user }) => user,
        view: ({ problemSet, user }) => new ContestProblemSetView(problemSet, user),
    },
};
