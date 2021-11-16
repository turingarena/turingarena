import { gql } from 'apollo-server-core';
import { ApiContext } from '../main/api-context';
import { ProblemTackling } from './contest-problem-assignment-user-tackling';
import { ProblemSetDefinition } from './contest-problem-set';
import { ScoreGrade } from './feedback/score';
import { User } from './user';
import { ProblemSetView } from './view/contest-problem-set-view';

export const problemSetTacklingSchema = gql`
    """
    The problem set of a given contest, tackled by a given user.
    """
    type ProblemSetTackling {
        "The problem set."
        problemSet: ProblemSetDefinition!
        "The given user."
        user: User!

        "Same problem-set seen by same user."
        view: ProblemSetView!

        assignmentTacklings: [ProblemTackling!]!

        totalScoreGrade: ScoreGrade!
    }
`;

export class ProblemSetTackling {
    constructor(readonly problemSet: ProblemSetDefinition, readonly user: User, readonly ctx: ApiContext) {}

    __typename = 'ProblemSetTackling' as const;

    view() {
        return new ProblemSetView(this.problemSet, this.user, this.ctx);
    }

    async totalScoreGrade() {
        const assignments = await this.problemSet.contest.getProblemAssignments();

        return ScoreGrade.total(
            await Promise.all(
                assignments.map(async assignment =>
                    new ProblemTackling(assignment, this.user, this.ctx).scoreGrade(),
                ),
            ),
        );
    }

    async assignmentTacklings() {
        const assignments = await this.problemSet.contest.getProblemAssignments();

        return assignments.map(assignment => new ProblemTackling(assignment, this.user, this.ctx));
    }
}
