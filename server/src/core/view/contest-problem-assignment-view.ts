import { gql } from 'apollo-server-core';
import { ApiContext } from '../../main/api-context';
import { ContestAwardAssignment } from '../contest-award-assignment';
import { ContestProblemAssignment } from '../contest-problem-assignment';
import { ContestProblemAssignmentUserTackling } from '../contest-problem-assignment-user-tackling';
import { ContestProblemSet } from '../contest-problem-set';
import { ScoreField } from '../feedback/score';
import { ProblemMaterialApi } from '../material/problem-material';
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

    __typename = 'ContestProblemAssignmentView';

    async problemSetView({}, ctx: ApiContext) {
        return new ContestProblemSetView(new ContestProblemSet(this.assignment.problem.contest), this.user, ctx);
    }

    async tackling({}, ctx: ApiContext) {
        return this.user !== null ? new ContestProblemAssignmentUserTackling(this.assignment, this.user, ctx) : null;
    }

    async totalScoreField({}, ctx: ApiContext) {
        const { scoreRange } = await ctx.api(ProblemMaterialApi).dataLoader.load(this.assignment.problem.id());
        const tackling = await this.tackling({}, ctx);

        const scoreGrade = tackling !== null ? await tackling.getScoreGrade() : null;

        return new ScoreField(scoreRange, scoreGrade?.score ?? null);
    }

    async awardAssignmentViews({}, ctx: ApiContext) {
        const { awards } = await ctx.api(ProblemMaterialApi).dataLoader.load(this.assignment.problem.id());

        return awards.map(
            award => new ContestAwardAssignmentView(new ContestAwardAssignment(this.assignment, award), this.user, ctx),
        );
    }
}

export interface ContestProblemAssignmentViewModelRecord {
    ContestProblemAssignmentView: ContestProblemAssignmentView;
}
