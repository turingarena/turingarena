import { gql } from 'apollo-server-core';
import { ApiContext } from '../main/api-context';
import { ObjectiveInstance } from './contest-objective-assignment';
import { ObjectiveTackling } from './contest-objective-assignment-user-tackling';
import { ProblemInstance } from './contest-problem-assignment';
import { ScoreGrade } from './feedback/score';
import { ProblemMaterialCache } from './material/problem-material';
import { SubmissionCache } from './submission';
import { User } from './user';
import { ProblemView } from './view/contest-problem-assignment-view';

export const problemTacklingSchema = gql`
    """
    Refers to a given problem, assigned in a given contest, tackled by a given user.
    Tackling means having a collection of submissions, and possibly submit a new one.
    This is separate from ProblemView since a ProblemTackling
    is available only for non-anonymous users who are allowed to have submissions (e.g., only after the contest is started).
    """
    type ProblemTackling {
        "User tackling the problem"
        user: User!

        "Same problem assigned in same contest"
        assignment: ProblemInstance!

        "Same problem assigned in same contest as seen by same user"
        assignmentView: ProblemView!

        "List of submissions for this problem in this contest from this user"
        submissions: [Submission!]!

        "Whether new submissions (see 'submissions') are accepted at the moment"
        canSubmit: Boolean!

        "Whether new submissions (see 'submissions') are accepted at the moment"
        scoreGrade: ScoreGrade!
    }
`;

export class ProblemTackling {
    constructor(readonly assignment: ProblemInstance, readonly user: User, readonly ctx: ApiContext) {}

    __typename = 'ProblemTackling' as const;

    id(): string {
        return `${this.assignment.id()}/${this.user.id}`;
    }

    static fromId(id: string, ctx: ApiContext): ProblemTackling {
        const ids = id.split('/');
        const assignmentId = ids.splice(0, 2).join('/');
        const userId = ids.join('/');

        return new ProblemTackling(
            ProblemInstance.fromId(assignmentId, ctx),
            User.fromId(userId, ctx),
            ctx,
        );
    }

    async canSubmit() {
        const status = await this.assignment.problem.contest.getStatus();

        return status === 'RUNNING';
    }

    async submissions() {
        return this.ctx.cache(SubmissionCache).byTackling.load(this.id());
    }

    assignmentView() {
        return new ProblemView(this.assignment, this.user, this.ctx);
    }

    async getObjectiveTacklings() {
        const material = await this.ctx.cache(ProblemMaterialCache).byId.load(this.assignment.problem.id());

        return material.objectives.map(
            objective =>
                new ObjectiveTackling(
                    new ObjectiveInstance(this.assignment, objective),
                    this.user,
                    this.ctx,
                ),
        );
    }

    async scoreGrade() {
        const objectiveTacklings = await this.getObjectiveTacklings();
        const objectiveGrades = await Promise.all(objectiveTacklings.map(t2 => t2.getGrade()));

        return ScoreGrade.total(objectiveGrades.filter((g): g is ScoreGrade => g instanceof ScoreGrade));
    }
}
