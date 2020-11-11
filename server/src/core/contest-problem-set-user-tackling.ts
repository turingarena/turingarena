import { gql } from 'apollo-server-core';
import { ApiObject } from '../main/api';
import { Resolvers } from '../main/resolver-types';
import { ContestApi } from './contest';
import {
    ContestProblemAssignmentUserTackling,
    ContestProblemAssignmentUserTacklingApi,
} from './contest-problem-assignment-user-tackling';
import { ContestProblemSet } from './contest-problem-set';
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
    __typename = 'ContestProblemSetUserTackling';
    view() {
        return { __typename: 'ContestProblemSetView', problemset: this.problemSet, user: this.user };
    }
}

export interface ContestProblemSetUserTacklingModelRecord {
    ContestProblemSetUserTackling: ContestProblemSetUserTackling;
}

export class ContestProblemSetUserTacklingApi extends ApiObject {
    async getScoreGrade({ problemSet, user }: ContestProblemSetUserTackling) {
        const assignments = await this.ctx.api(ContestApi).getProblemAssignments(problemSet.contest);

        return ScoreGrade.total(
            await Promise.all(
                assignments.map(async assignment =>
                    this.ctx
                        .api(ContestProblemAssignmentUserTacklingApi)
                        .getScoreGrade(new ContestProblemAssignmentUserTackling(assignment, user)),
                ),
            ),
        );
    }
}

