import { gql } from 'apollo-server-core';
import { ApiContext } from '../main/api-context';
import { ScoreGrade } from './data/score';
import { ObjectiveInstance } from './objective-instance';
import { ObjectiveTackling } from './objective-tackling';
import { ProblemMaterialCache } from './problem-definition-material';
import { ProblemInstance } from './problem-instance';
import { ProblemView } from './problem-view';
import { SubmissionCache } from './submission';
import { User } from './user';

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
        instance: ProblemInstance!

        "Same problem assigned in same contest as seen by same user"
        view: ProblemView!

        "List of submissions for this problem in this contest from this user"
        submissions: [Submission!]!

        "Whether new submissions (see 'submissions') are accepted at the moment"
        canSubmit: Boolean!

        "Current total score on this problem"
        totalScoreGrade: ScoreGrade!
    }
`;

export class ProblemTackling {
    constructor(readonly instance: ProblemInstance, readonly user: User, readonly ctx: ApiContext) {}

    __typename = 'ProblemTackling' as const;

    id(): string {
        return `${this.instance.id()}/${this.user.id}`;
    }

    static fromId(id: string, ctx: ApiContext): ProblemTackling {
        const ids = id.split('/');
        const problemId = ids.splice(0, 2).join('/');
        const userId = ids.join('/');

        return new ProblemTackling(ProblemInstance.fromId(problemId, ctx), User.fromId(userId, ctx), ctx);
    }

    async canSubmit() {
        const status = await this.instance.definition.contest.getStatus();

        return status === 'RUNNING';
    }

    async submissions() {
        return this.ctx.cache(SubmissionCache).byTackling.load(this.id());
    }

    view() {
        return new ProblemView(this.instance, this.user, this.ctx);
    }

    async getObjectiveTacklings() {
        const material = await this.ctx.cache(ProblemMaterialCache).byId.load(this.instance.definition.id());

        return material.objectives.map(
            objective => new ObjectiveTackling(new ObjectiveInstance(this.instance, objective), this.user, this.ctx),
        );
    }

    async totalScoreGrade() {
        const objectiveTacklings = await this.getObjectiveTacklings();
        const objectiveGrades = await Promise.all(objectiveTacklings.map(t2 => t2.getGrade()));

        return ScoreGrade.total(objectiveGrades.filter((g): g is ScoreGrade => g instanceof ScoreGrade));
    }
}
