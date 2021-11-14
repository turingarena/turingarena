import { gql } from 'apollo-server-core';
import { ApiContext } from '../main/api-context';
import { ContestProblemAssignmentUserTackling } from './contest-problem-assignment-user-tackling';
import { ContestProblemSet } from './contest-problem-set';
import { ScoreGrade } from './feedback/score';
import { User } from './user';
import { ContestProblemSetView } from './view/contest-problem-set-view';

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

        assignmentTacklings: [ContestProblemAssignmentUserTackling!]!

        totalScoreGrade: ScoreGrade!
    }
`;

export class ContestProblemSetUserTackling {
    constructor(readonly problemSet: ContestProblemSet, readonly user: User, readonly ctx: ApiContext) { }

    __typename = 'ContestProblemSetUserTackling' as const;

    view() {
        return new ContestProblemSetView(this.problemSet, this.user, this.ctx);
    }

    async totalScoreGrade() {
        const assignments = await this.problemSet.contest.getProblemAssignments();

        return ScoreGrade.total(
            await Promise.all(
                assignments.map(async assignment =>
                    new ContestProblemAssignmentUserTackling(assignment, this.user, this.ctx).scoreGrade(),
                ),
            ),
        );
    }

    async assignmentTacklings() {
        const assignments = await this.problemSet.contest.getProblemAssignments();

        return assignments.map(assignment => new ContestProblemAssignmentUserTackling(assignment, this.user, this.ctx));
    }
}

export interface ContestProblemSetUserTacklingModelRecord {
    ContestProblemSetUserTackling: ContestProblemSetUserTackling;
}
