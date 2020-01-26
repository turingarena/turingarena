import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../main/resolver-types';
import { ContestAwardAssignment } from './contest-award-assignment';
import { ContestProblemAssignmentView } from './contest-problem-assignment-view';
import { FulfillmentDomain } from './feedback/fulfillment';
import { ScoreDomain } from './feedback/score';
import { User } from './user';

export const contestAwardAssignmentViewSchema = gql`
    type ContestAwardAssignmentView {
        assignment: ContestAwardAssignment!
        user: User
        problemAssignmentView: ContestProblemAssignmentView!

        gradeVariable: GradeVariable!
    }
`;

export class ContestAwardAssignmentView {
    constructor(readonly assignment: ContestAwardAssignment, readonly user: User | null) {}

    async getGradeVariable() {
        const { gradeDomain: domain } = this.assignment.award;

        if (domain instanceof FulfillmentDomain) {
            return domain.createVariable(
                this.user !== null
                    ? (await this.assignment.getBestAchievement(this.user))?.toFulfillmentValue() ?? false
                    : null,
            );
        }

        if (domain instanceof ScoreDomain) {
            return domain.createVariable(
                this.user !== null
                    ? (await this.assignment.getBestAchievement(this.user))?.toScoreValue(domain) ?? domain.zero()
                    : null,
            );
        }

        throw new Error(`unexpected grade domain ${domain}`);
    }
}

export const contestAwardAssignmentViewResolvers: ResolversWithModels<{
    ContestAwardAssignmentView: ContestAwardAssignmentView;
}> = {
    ContestAwardAssignmentView: {
        assignment: ({ assignment }) => assignment,
        user: ({ user }) => user,
        problemAssignmentView: async ({ assignment, user }) =>
            new ContestProblemAssignmentView(assignment.problemAssignment, user),
        gradeVariable: view => view.getGradeVariable(),
    },
};
