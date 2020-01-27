import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../main/resolver-types';
import { ContestAwardAssignment } from './contest-award-assignment';
import { ContestAwardAssignmentUserTackling } from './contest-award-assignment-user-tackling';
import { ContestProblemAssignmentView } from './contest-problem-assignment-view';
import { FulfillmentField, FulfillmentGradeDomain } from './feedback/fulfillment';
import { ScoreField, ScoreGradeDomain } from './feedback/score';
import { User } from './user';

export const contestAwardAssignmentViewSchema = gql`
    """
    Refers to a given award of a problem, assigned in a given contest, as seen by a given user or anonymously.
    """
    type ContestAwardAssignmentView {
        "Same award assigned in same contest."
        assignment: ContestAwardAssignment!
        "User viewing this, or null if anonymous."
        user: User
        "The problem containing the given award, assigned in same contest, as seen by same user or anonymously"
        problemAssignmentView: ContestProblemAssignmentView!

        "Current grade for this award in this contest, to show to the given user."
        gradeField: GradeField!
    }
`;

export class ContestAwardAssignmentView {
    constructor(readonly assignment: ContestAwardAssignment, readonly user: User | null) {}

    tackling = this.user !== null ? new ContestAwardAssignmentUserTackling(this.assignment, this.user) : null;

    async getGradeField() {
        const { gradeDomain: domain } = this.assignment.award;

        if (domain instanceof FulfillmentGradeDomain) {
            const grade = await this.tackling?.getFulfillmentGrade();

            return new FulfillmentField(grade?.fulfilled ?? null);
        }

        if (domain instanceof ScoreGradeDomain) {
            const grade = await this.tackling?.getScoreGrade(domain);

            return new ScoreField(domain.scoreRange, grade?.score ?? null);
        }

        throw new Error(`unexpected grade domain ${domain}`);
    }
}

export const contestAwardAssignmentViewResolvers: ResolversWithModels<{
    ContestAwardAssignmentView: ContestAwardAssignmentView;
}> = {
    ContestAwardAssignmentView: {
        assignment: view => view.assignment,
        user: view => view.user,
        problemAssignmentView: async ({ assignment, user }) =>
            new ContestProblemAssignmentView(assignment.problemAssignment, user),
        gradeField: view => view.getGradeField(),
    },
};
