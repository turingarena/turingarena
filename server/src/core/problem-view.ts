import { gql } from 'apollo-server-core';
import { ApiContext } from '../main/api-context';
import { ScoreField } from './data/score';
import { ObjectiveInstance } from './objective-instance';
import { ObjectiveView } from './objective-view';
import { ProblemMaterialCache } from './problem-definition-material';
import { ProblemInstance } from './problem-instance';
import { ProblemSetDefinition } from './problem-set-definition';
import { ProblemSetView } from './problem-set-view';
import { ProblemUndertaking } from './problem-undertaking';
import { User } from './user';

export const problemViewSchema = gql`
    """
    Refers to a given problem, assigned in a given contest, as seen by a given user or anonymously.
    """
    type ProblemView {
        "Same problem assigned in same contest"
        instance: ProblemInstance!
        "Viewing user, or null if anonymous"
        user: User

        "Set of problems in same contest, as seen by same user"
        problemSet: ProblemSetView!

        """
        Same problem assigned in same contest tackled by same user,
        if the user is non-anonymous and allowed to have submissions for this problem in this contest,
        and null otherwise.
        """
        undertaking: ProblemUndertaking

        "Current score seen by the user for this problem in this contest."
        totalScoreField: ScoreField!

        "Objectives of this problem assigned in same contest as seen by same user (or anonymously)"
        objectives: [ObjectiveView!]!
    }
`;

export class ProblemView {
    constructor(readonly instance: ProblemInstance, readonly user: User | null, readonly ctx: ApiContext) {}

    __typename = 'ProblemView' as const;

    async problemSet() {
        return new ProblemSetView(new ProblemSetDefinition(this.instance.definition.contest), this.user, this.ctx);
    }

    async undertaking() {
        return this.user !== null ? new ProblemUndertaking(this.instance, this.user, this.ctx) : null;
    }

    async totalScoreField() {
        const { scoreRange } = await this.ctx.cache(ProblemMaterialCache).byId.load(this.instance.definition.id());
        const undertaking = await this.undertaking();

        const scoreGrade = undertaking !== null ? await undertaking.totalScoreGrade() : null;

        return new ScoreField(scoreRange, scoreGrade?.score ?? null);
    }

    async objectives() {
        const { objectives } = await this.ctx.cache(ProblemMaterialCache).byId.load(this.instance.definition.id());

        return objectives.map(
            objective => new ObjectiveView(new ObjectiveInstance(this.instance, objective), this.user, this.ctx),
        );
    }
}
