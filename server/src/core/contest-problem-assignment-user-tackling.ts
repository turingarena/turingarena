import { gql } from 'apollo-server-core';
import { ApiObject } from '../main/api';
import { Resolvers } from '../main/resolver-types';
import { ContestApi } from './contest';
import { ContestAwardAssignment } from './contest-award-assignment';
import {
    ContestAwardAssignmentUserTackling,
    ContestAwardAssignmentUserTacklingApi,
} from './contest-award-assignment-user-tackling';
import { ContestProblemAssignment } from './contest-problem-assignment';
import { ContestProblemAssignmentView } from './contest-problem-assignment-view';
import { ScoreGrade } from './feedback/score';
import { ProblemApi } from './problem';
import { SubmissionApi } from './submission';
import { User } from './user';

export const contestProblemAssignmentUserTacklingSchema = gql`
    """
    Refers to a given problem, assigned in a given contest, tackled by a given user.
    Tackling means having a collection of submissions, and possibly submit a new one.
    This is separate from ContestProblemAssignmentView since a ContestProblemAssignmentUserTackling
    is available only for non-anonymous users who are allowed to have submissions (e.g., only after the contest is started).
    """
    type ContestProblemAssignmentUserTackling {
        "Same problem assigned in same contest as seen by same user"
        assignmentView: ContestProblemAssignmentView!

        "User tackling the problem"
        user: User!

        "List of submissions for this problem in this contest from this user"
        submissions: [Submission!]!

        "Whether new submissions (see 'submissions') are accepted at the moment"
        canSubmit: Boolean!
    }
`;

export class ContestProblemAssignmentUserTackling {
    constructor(readonly assignment: ContestProblemAssignment, readonly user: User) {}
}

export interface ContestProblemAssignmentUserTacklingModelRecord {
    ContestProblemAssignmentUserTackling: ContestProblemAssignmentUserTackling;
}

export class ContestProblemAssignmentUserTacklingApi extends ApiObject {
    async canSubmit(t: ContestProblemAssignmentUserTackling) {
        const contest = await this.ctx.api(ContestApi).byId.load(t.assignment.contestId);
        const status = this.ctx.api(ContestApi).getStatus(contest);

        return status === 'RUNNING';
    }

    async getAwardTacklings(t: ContestProblemAssignmentUserTackling) {
        const problem = await this.ctx.api(ProblemApi).byId.load(t.assignment.problemId);
        const material = await problem.getMaterial();

        return material.awards.map(
            award => new ContestAwardAssignmentUserTackling(new ContestAwardAssignment(t.assignment, award), t.user),
        );
    }

    async getScoreGrade(t: ContestProblemAssignmentUserTackling) {
        const awardTacklings = await this.getAwardTacklings(t);
        const awardGrades = await Promise.all(
            awardTacklings.map(t2 => this.ctx.api(ContestAwardAssignmentUserTacklingApi).getGrade(t2)),
        );

        return ScoreGrade.total(awardGrades.filter((g): g is ScoreGrade => g instanceof ScoreGrade));
    }
}

export const contestProblemAssignmentUserTacklingResolvers: Resolvers = {
    ContestProblemAssignmentUserTackling: {
        canSubmit: async (t, {}, ctx) => ctx.api(ContestProblemAssignmentUserTacklingApi).canSubmit(t),
        submissions: async ({ assignment: { contestId, problemId }, user: { id: userId } }, {}, ctx) =>
            ctx.api(SubmissionApi).allByTackling.load({ problemId, contestId, userId }),
        assignmentView: ({ assignment, user }) => new ContestProblemAssignmentView(assignment, user),
        user: ({ user }) => user,
    },
};
