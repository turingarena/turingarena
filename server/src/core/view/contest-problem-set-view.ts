import { gql } from 'apollo-server-core';
import { ApiContext } from '../../main/api-context';
import { ContestApi } from '../contest';
import { ContestProblemSet } from '../contest-problem-set';
import { ContestProblemSetUserTackling } from '../contest-problem-set-user-tackling';
import { ScoreField } from '../feedback/score';
import { User } from '../user';
import { ContestProblemAssignmentView } from './contest-problem-assignment-view';
import { ContestView } from './contest-view';

export const contestProblemSetViewSchema = gql`
    """
    The problem-set of a given contest, as seen by a given user or anonymously.
    """
    type ContestProblemSetView {
        "The problem-set of the same contest."
        problemSet: ContestProblemSet!
        "The given user, if any, or null if anonymous."
        user: User
        "Same contest, as seen by the same user (or anonymously)."
        contestView: ContestView!
        "The list of problems in the given problem-set, assigned in the same contest, as seen by the same user (or anonymously)."
        assignmentViews: [ContestProblemAssignmentView!]!

        "Same contest as tackled by the same user, or null if anonymous."
        tackling: ContestProblemSetUserTackling

        "Current total score visible to the given user."
        totalScoreField: ScoreField!
    }
`;

export class ContestProblemSetView {
    constructor(readonly problemSet: ContestProblemSet, readonly user: User | null) {}

    __typename = 'ContestProblemSetView';

    contestView() {
        return new ContestView(this.problemSet.contest, this.user);
    }

    async assignmentViews({}, ctx: ApiContext) {
        return (await ctx.api(ContestApi).getProblemAssignments(this.problemSet.contest)).map(
            assignment => new ContestProblemAssignmentView(assignment, this.user),
        );
    }

    tackling() {
        if (this.user === null) return null;

        return new ContestProblemSetUserTackling(this.problemSet, this.user);
    }

    async totalScoreField({}, ctx: ApiContext) {
        const tackling = this.tackling();

        const scoreRange = await this.problemSet.getScoreRange(ctx);
        const scoreGrade = tackling !== null ? await tackling.getScoreGrade(ctx) : null;

        return new ScoreField(scoreRange, scoreGrade?.score ?? null);
    }
}

export interface ContestProblemSetViewModelRecord {
    ContestProblemSetView: ContestProblemSetView;
}
