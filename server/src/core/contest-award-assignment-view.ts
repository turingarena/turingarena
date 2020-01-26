import { gql } from 'apollo-server-core';
import { GradeVariable } from '../generated/graphql-types';
import { ResolversWithModels } from '../main/resolver-types';
import { ContestAwardAssignment } from './contest-award-assignment';
import { ContestProblemAssignmentView } from './contest-problem-assignment-view';
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

    async getGradeVariable(): Promise<GradeVariable> {
        const { gradeDomain: domain } = this.assignment.award;

        switch (domain.__typename) {
            case 'FulfillmentDomain':
                return {
                    __typename: 'FulfillmentVariable',
                    domain,
                    value:
                        this.user !== null
                            ? (await this.assignment.getBestAchievement(this.user))?.toFulfillmentValue(domain) ?? {
                                  __typename: 'FulfillmentValue',
                                  domain,
                                  fulfilled: false,
                                  valence: 'FAILURE',
                              }
                            : null,
                };
            case 'ScoreDomain':
                return {
                    __typename: 'ScoreVariable',
                    domain,
                    value:
                        this.user !== null
                            ? (await this.assignment.getBestAchievement(this.user))?.toScoreValue(domain) ?? {
                                  __typename: 'ScoreValue',
                                  domain,
                                  score: 0,
                                  valence: 'FAILURE',
                              }
                            : null,
                };
            default:
                throw new Error();
        }
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
