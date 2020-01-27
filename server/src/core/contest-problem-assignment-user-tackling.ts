import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../main/resolver-types';
import { ContestAwardAssignment } from './contest-award-assignment';
import { ContestAwardAssignmentUserTackling } from './contest-award-assignment-user-tackling';
import { ContestProblemAssignment } from './contest-problem-assignment';
import { ContestProblemAssignmentView } from './contest-problem-assignment-view';
import { ScoreValue } from './feedback/score';
import { Submission } from './submission';
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

    async getAwardTacklings() {
        const problem = await this.assignment.getProblem();
        const material = await problem.getMaterial();

        return material.awards.map(
            award =>
                new ContestAwardAssignmentUserTackling(new ContestAwardAssignment(this.assignment, award), this.user),
        );
    }

    async getScore() {
        const awardTacklings = await this.getAwardTacklings();
        const awardGrades = await Promise.all(awardTacklings.map(t => t.getGrade()));

        return ScoreValue.total(awardGrades.filter((g): g is ScoreValue => g instanceof ScoreValue));
    }
}

export const contestProblemAssignmentUserTacklingResolvers: ResolversWithModels<{
    ContestProblemAssignmentUserTackling: ContestProblemAssignmentUserTackling;
}> = {
    ContestProblemAssignmentUserTackling: {
        canSubmit: async ({ assignment }) => (await assignment.getContest()).getStatus() === 'RUNNING',
        submissions: async ({ assignment: { contestId, problemId }, user: { id: userId, root } }) =>
            root.table(Submission).findAll({ where: { problemId, contestId, userId } }),
        assignmentView: ({ assignment, user }) => new ContestProblemAssignmentView(assignment, user),
        user: ({ user }) => user,
    },
};
