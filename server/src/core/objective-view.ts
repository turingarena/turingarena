import { gql } from 'apollo-server-core';
import { ApiContext } from '../main/api-context';
import { ApiOutputValue } from '../main/graphql-types';
import { FulfillmentField, FulfillmentGradeDomain } from './data/fulfillment';
import { ScoreField, ScoreGradeDomain } from './data/score';
import { ObjectiveInstance } from './objective-instance';
import { ObjectiveUndertaking } from './objective-undertaking';
import { ProblemView } from './problem-view';
import { User } from './user';

export const objectiveViewSchema = gql`
    """
    Refers to a given objective of a problem, assigned in a given contest, as seen by a given user or anonymously.
    """
    type ObjectiveView {
        "Same objective assigned in same contest."
        instance: ObjectiveInstance!
        "User viewing this, or null if anonymous."
        user: User
        "The problem containing the given objective, assigned in same contest, as seen by same user or anonymously"
        problem: ProblemView!

        "Current grade for this objective in this contest, to show to the given user."
        gradeField: GradeField!
    }
`;

export class ObjectiveView implements ApiOutputValue<'ObjectiveView'> {
    constructor(readonly instance: ObjectiveInstance, readonly user: User | null, readonly ctx: ApiContext) {}

    __typename = 'ObjectiveView' as const;

    async problem() {
        return new ProblemView(this.instance.problem, this.user, this.ctx);
    }

    async gradeField() {
        const { gradeDomain: domain } = this.instance.definition;
        const undertaking = this.getUndertaking();

        if (domain instanceof FulfillmentGradeDomain) {
            const grade = undertaking !== null ? await undertaking.getFulfillmentGrade() : null;

            return new FulfillmentField(grade?.fulfilled ?? null);
        }

        if (domain instanceof ScoreGradeDomain) {
            const grade = undertaking !== null ? await undertaking.getScoreGrade(domain) : null;

            return new ScoreField(domain.scoreRange, grade?.score ?? null);
        }

        throw new Error(`unexpected grade domain ${domain}`);
    }

    getUndertaking() {
        if (this.user === null) return null;

        return new ObjectiveUndertaking(this.instance, this.user, this.ctx);
    }
}
