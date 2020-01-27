import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../main/resolver-types';
import { ContestProblemAssignmentView } from './contest-problem-assignment-view';
import { ContestProblemSet } from './contest-problem-set';
import { ContestProblemSetUserTackling } from './contest-problem-set-user-tackling';
import { ContestView } from './contest-view';
import { ScoreField } from './feedback/score';
import { User } from './user';

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

    readonly tackling = this.user !== null ? new ContestProblemSetUserTackling(this.problemSet, this.user) : null;

    async getTotalScoreField() {
        return new ScoreField(
            await this.problemSet.getScoreRange(),
            (await this.tackling?.getScoreGrade())?.score ?? null,
        );
    }
}

export const contestProblemSetViewResolvers: ResolversWithModels<{
    ContestProblemSetView: ContestProblemSetView;
}> = {
    ContestProblemSetView: {
        problemSet: ({ problemSet }) => problemSet,
        user: ({ user }) => user,
        contestView: ({ problemSet, user }) => new ContestView(problemSet.contest, user),
        assignmentViews: async ({ problemSet, user }) =>
            (await problemSet.contest.getProblemAssignments()).map(a => new ContestProblemAssignmentView(a, user)),
        tackling: ({ problemSet, user }) =>
            user !== null ? new ContestProblemSetUserTackling(problemSet, user) : null,
        totalScoreField: async view => view.getTotalScoreField(),
    },
};
