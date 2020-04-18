import { gql } from 'apollo-server-core';
import { ApiObject } from '../../main/api';
import { Resolvers } from '../../main/resolver-types';
import { ContestApi } from '../contest';
import { ContestAwardAssignment } from '../contest-award-assignment';
import { ContestProblemAssignment } from '../contest-problem-assignment';
import {
    ContestProblemAssignmentUserTackling,
    ContestProblemAssignmentUserTacklingApi,
} from '../contest-problem-assignment-user-tackling';
import { ContestProblemSet } from '../contest-problem-set';
import { ScoreField } from '../feedback/score';
import { ProblemMaterialApi } from '../material/problem-material';
import { Problem } from '../problem';
import { User } from '../user';
import { ContestAwardAssignmentView } from './contest-award-assignment-view';
import { ContestProblemSetView } from './contest-problem-set-view';

export const contestProblemAssignmentViewSchema = gql`
    """
    Refers to a given problem, assigned in a given contest, as seen by a given user or anonymously.
    """
    type ContestProblemAssignmentView {
        "Same problem assigned in same contest"
        assignment: ContestProblemAssignment!
        "Viewing user, or null if anonymous"
        user: User

        "Set of problems in same contest, as seen by same user"
        problemSetView: ContestProblemSetView!

        """
        Same problem assigned in same contest tackled by same user,
        if the user is non-anonymous and allowed to have submissions for this problem in this contest,
        and null otherwise.
        """
        tackling: ContestProblemAssignmentUserTackling

        "Current score seen by the user for this problem in this contest."
        totalScoreField: ScoreField!

        "Awards of this problem assigned in same contest as seen by same user (or anonymously)"
        awardAssignmentViews: [ContestAwardAssignmentView!]!
    }
`;

export class ContestProblemAssignmentView {
    constructor(readonly assignment: ContestProblemAssignment, readonly user: User | null) {}

    tackling = this.user !== null ? new ContestProblemAssignmentUserTackling(this.assignment, this.user) : null;
}

export interface ContestProblemAssignmentViewModelRecord {
    ContestProblemAssignmentView: ContestProblemAssignmentView;
}

export class ContestProblemAssignmentViewApi extends ApiObject {
    async getProblem({ assignment: { contestId, problemName } }: ContestProblemAssignmentView) {
        return new Problem(contestId, problemName);
    }

    async getContest({ assignment: { contestId } }: ContestProblemAssignmentView) {
        return this.ctx.api(ContestApi).byId.load(contestId);
    }

    async getTotalScoreField(view: ContestProblemAssignmentView) {
        const { scoreRange } = await this.ctx.api(ProblemMaterialApi).byContestAndProblemName.load({
            contestId: view.assignment.contestId,
            problemName: view.assignment.problemName,
        });

        const scoreGrade =
            view.tackling !== null
                ? await this.ctx.api(ContestProblemAssignmentUserTacklingApi).getScoreGrade(view.tackling)
                : null;

        return new ScoreField(scoreRange, scoreGrade?.score ?? null);
    }

    async getAwardAssignmentViews(view: ContestProblemAssignmentView) {
        const { awards } = await this.ctx.api(ProblemMaterialApi).byContestAndProblemName.load({
            contestId: view.assignment.contestId,
            problemName: view.assignment.problemName,
        });

        return awards.map(
            award => new ContestAwardAssignmentView(new ContestAwardAssignment(view.assignment, award), view.user),
        );
    }

    async getProblemSetView(view: ContestProblemAssignmentView) {
        const contest = await this.getContest(view);

        return new ContestProblemSetView(new ContestProblemSet(contest), view.user);
    }
}

export const contestProblemAssignmentViewResolvers: Resolvers = {
    ContestProblemAssignmentView: {
        assignment: v => v.assignment,
        user: v => v.user,
        problemSetView: async (v, {}, ctx) => ctx.api(ContestProblemAssignmentViewApi).getProblemSetView(v),
        tackling: async ({ assignment, user }) =>
            user !== null ? new ContestProblemAssignmentUserTackling(assignment, user) : null,
        totalScoreField: async (v, {}, ctx) => ctx.api(ContestProblemAssignmentViewApi).getTotalScoreField(v),
        awardAssignmentViews: async (v, {}, ctx) => ctx.api(ContestProblemAssignmentViewApi).getAwardAssignmentViews(v),
    },
};
