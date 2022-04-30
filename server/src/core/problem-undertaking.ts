import { gql } from 'apollo-server-core';
import { ApiContext } from '../main/api-context';
import { ApiOutputValue } from '../main/graphql-types';
import { ScoreGrade } from './data/score';
import { ObjectiveInstance } from './objective-instance';
import { ObjectiveUndertaking } from './objective-undertaking';
import { ProblemMaterialCache } from './problem-definition-material';
import { ProblemInstance } from './problem-instance';
import { ProblemView } from './problem-view';
import { SubmissionCache } from './submission';
import { User } from './user';

export const problemUndertakingSchema = gql`
    """
    Refers to a given problem, assigned in a given contest, tackled by a given user.
    Undertaking means having a collection of submissions, and possibly submit a new one.
    This is separate from ProblemView since a ProblemUndertaking
    is available only for non-anonymous users who are allowed to have submissions (e.g., only after the contest is started).
    """
    type ProblemUndertaking {
        "User undertaking the problem"
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

export class ProblemUndertaking implements ApiOutputValue<'ProblemUndertaking'> {
    constructor(readonly instance: ProblemInstance, readonly user: User, readonly ctx: ApiContext) {}

    __typename = 'ProblemUndertaking' as const;
    id = `${this.instance.id}/${this.user.id}`;

    static async fromId(id: string, ctx: ApiContext) {
        const ids = id.split('/');
        const problemId = ids.splice(0, 2).join('/');
        const userId = ids.join('/');

        return new ProblemUndertaking(ProblemInstance.fromId(problemId, ctx), await User.fromId(userId, ctx), ctx);
    }

    async canSubmit() {
        const status = await this.instance.definition.contest.getStatus();

        return status === 'RUNNING';
    }

    async submissions() {
        return this.ctx.cache(SubmissionCache).byUndertaking.load(this.id);
    }

    view() {
        return new ProblemView(this.instance, this.user, this.ctx);
    }

    async getObjectiveUndertakings() {
        const material = await this.ctx.cache(ProblemMaterialCache).byId.load(this.instance.definition.id);

        return material.objectives.map(
            objective => new ObjectiveUndertaking(new ObjectiveInstance(this.instance, objective), this.user, this.ctx),
        );
    }

    async totalScoreGrade() {
        const objectiveUndertakings = await this.getObjectiveUndertakings();
        const objectiveGrades = await Promise.all(objectiveUndertakings.map(t2 => t2.getGrade()));

        return ScoreGrade.total(objectiveGrades.filter((g): g is ScoreGrade => g instanceof ScoreGrade));
    }
}
