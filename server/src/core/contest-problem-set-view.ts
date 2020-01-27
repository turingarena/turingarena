import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../main/resolver-types';
import { ContestProblemAssignmentView } from './contest-problem-assignment-view';
import { ContestProblemSetUserTackling } from './contest-problem-set-user-tackling';
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
        totalScoreVariable: ScoreVariable!
    }
`;

export const contestProblemSetViewResolvers: ResolversWithModels<{
    ContestProblemSetView: ContestView;
}> = {
    ContestProblemSetView: {
        problemSet: view => view.contest,
        user: view => view.user,
        contestView: view => view,
        assignmentViews: async ({ contest, user }) =>
            (await contest.getProblemAssignments()).map(a => new ContestProblemAssignmentView(a, user)),
        tackling: ({ contest, user }) => (user !== null ? new ContestProblemSetUserTackling(contest, user) : null),
        totalScoreVariable: async view => view.getTotalScoreVariable(),
    },
};
