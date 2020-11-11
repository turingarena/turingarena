import { gql } from 'apollo-server-core';
import { ApiObject } from '../../main/api';
import { Resolvers } from '../../main/resolver-types';
import { typed } from '../../util/types';
import { ContestApi } from '../contest';
import { ContestProblemSet, ContestProblemSetApi } from '../contest-problem-set';
import { ContestProblemSetUserTackling, ContestProblemSetUserTacklingApi } from '../contest-problem-set-user-tackling';
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

export interface ContestProblemSetView {
    __typename: 'ContestProblemSetView';
    problemSet: ContestProblemSet;
    user: User | null;
}

export interface ContestProblemSetViewModelRecord {
    ContestProblemSetView: ContestProblemSetView;
}

export class ContestProblemSetViewApi extends ApiObject {
    getTackling({ problemSet, user }: ContestProblemSetView) {
        if (user === null) return null;

        return new ContestProblemSetUserTackling(problemSet, user);
    }

    async getTotalScoreField(v: ContestProblemSetView) {
        const tackling = this.getTackling(v);

        const scoreRange = await this.ctx.api(ContestProblemSetApi).getScoreRange(v.problemSet);
        const scoreGrade =
            tackling !== null ? await this.ctx.api(ContestProblemSetUserTacklingApi).getScoreGrade(tackling) : null;

        return new ScoreField(scoreRange, scoreGrade?.score ?? null);
    }
}

export const contestProblemSetViewResolvers: Resolvers = {
    ContestProblemSetView: {
        problemSet: v => v.problemSet,
        user: v => v.user,
        contestView: ({ problemSet: { contest }, user }) =>
            typed<ContestView>({ __typename: 'ContestView', contest, user }),
        assignmentViews: async ({ problemSet, user }, {}, ctx) =>
            (await ctx.api(ContestApi).getProblemAssignments(problemSet.contest)).map(
                assignment => new ContestProblemAssignmentView(assignment, user),
            ),
        tackling: (v, {}, ctx) => ctx.api(ContestProblemSetViewApi).getTackling(v),
        totalScoreField: async (v, {}, ctx) => ctx.api(ContestProblemSetViewApi).getTotalScoreField(v),
    },
};
