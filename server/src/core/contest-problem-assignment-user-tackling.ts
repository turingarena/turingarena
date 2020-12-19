import { gql } from 'apollo-server-core';
import { ApiContext } from '../main/api-context';
import { ContestAwardAssignment } from './contest-award-assignment';
import { ContestAwardAssignmentUserTackling } from './contest-award-assignment-user-tackling';
import { ContestProblemAssignment } from './contest-problem-assignment';
import { ScoreGrade } from './feedback/score';
import { ProblemMaterialApi } from './material/problem-material';
import { SubmissionCache } from './submission';
import { User } from './user';
import { ContestProblemAssignmentView } from './view/contest-problem-assignment-view';

export const contestProblemAssignmentUserTacklingSchema = gql`
    """
    Refers to a given problem, assigned in a given contest, tackled by a given user.
    Tackling means having a collection of submissions, and possibly submit a new one.
    This is separate from ContestProblemAssignmentView since a ContestProblemAssignmentUserTackling
    is available only for non-anonymous users who are allowed to have submissions (e.g., only after the contest is started).
    """
    type ContestProblemAssignmentUserTackling {
        "User tackling the problem"
        user: User!

        "Same problem assigned in same contest"
        assignment: ContestProblemAssignment!

        "Same problem assigned in same contest as seen by same user"
        assignmentView: ContestProblemAssignmentView!

        "List of submissions for this problem in this contest from this user"
        submissions: [Submission!]!

        "Whether new submissions (see 'submissions') are accepted at the moment"
        canSubmit: Boolean!

        "Whether new submissions (see 'submissions') are accepted at the moment"
        scoreGrade: ScoreGrade!
    }
`;

export class ContestProblemAssignmentUserTackling {
    constructor(readonly assignment: ContestProblemAssignment, readonly user: User, readonly ctx: ApiContext) {}

    __typename = 'ContestProblemAssignmentUserTackling';

    id(): string {
        return `${this.assignment.id()}/${this.user.id()}`;
    }

    static fromId(id: string, ctx: ApiContext): ContestProblemAssignmentUserTackling {
        const ids = id.split('/');
        const assignmentId = ids.splice(0, 2).join('/');
        const userId = ids.join('/');

        return new ContestProblemAssignmentUserTackling(
            ContestProblemAssignment.fromId(assignmentId, ctx),
            User.fromId(userId, ctx),
            ctx,
        );
    }

    async canSubmit() {
        const status = await this.assignment.problem.contest.getStatus();

        return status === 'RUNNING';
    }

    async submissions() {
        return this.ctx.api(SubmissionCache).allByTackling.load(this.id());
    }

    assignmentView() {
        return new ContestProblemAssignmentView(this.assignment, this.user, this.ctx);
    }

    async getAwardTacklings() {
        const material = await this.ctx.api(ProblemMaterialApi).dataLoader.load(this.assignment.problem.id());

        return material.awards.map(
            award =>
                new ContestAwardAssignmentUserTackling(
                    new ContestAwardAssignment(this.assignment, award),
                    this.user,
                    this.ctx,
                ),
        );
    }

    async scoreGrade() {
        const awardTacklings = await this.getAwardTacklings();
        const awardGrades = await Promise.all(awardTacklings.map(t2 => t2.getGrade()));

        return ScoreGrade.total(awardGrades.filter((g): g is ScoreGrade => g instanceof ScoreGrade));
    }
}

export interface ContestProblemAssignmentUserTacklingModelRecord {
    ContestProblemAssignmentUserTackling: ContestProblemAssignmentUserTackling;
}
