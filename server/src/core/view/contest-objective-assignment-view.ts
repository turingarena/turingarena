import { gql } from 'apollo-server-core';
import { ApiContext } from '../../main/api-context';
import { ObjectiveInstance } from '../contest-objective-assignment';
import { ObjectiveTackling } from '../contest-objective-assignment-user-tackling';
import { FulfillmentField, FulfillmentGradeDomain } from '../feedback/fulfillment';
import { ScoreField, ScoreGradeDomain } from '../feedback/score';
import { User } from '../user';
import { ProblemView } from './contest-problem-assignment-view';

export const objectiveViewSchema = gql`
    """
    Refers to a given objective of a problem, assigned in a given contest, as seen by a given user or anonymously.
    """
    type ObjectiveView {
        "Same objective assigned in same contest."
        assignment: ObjectiveInstance!
        "User viewing this, or null if anonymous."
        user: User
        "The problem containing the given objective, assigned in same contest, as seen by same user or anonymously"
        problemAssignmentView: ProblemView!

        "Current grade for this objective in this contest, to show to the given user."
        gradeField: GradeField!
    }
`;

export class ObjectiveView {
    constructor(readonly assignment: ObjectiveInstance, readonly user: User | null, readonly ctx: ApiContext) {}

    __typename = 'ObjectiveView' as const;

    async problemAssignmentView() {
        return new ProblemView(this.assignment.problemAssignment, this.user, this.ctx);
    }

    async gradeField() {
        const { gradeDomain: domain } = this.assignment.objective;
        const tackling = this.getTackling();

        if (domain instanceof FulfillmentGradeDomain) {
            const grade = tackling !== null ? await tackling.getFulfillmentGrade() : null;

            return new FulfillmentField(grade?.fulfilled ?? null);
        }

        if (domain instanceof ScoreGradeDomain) {
            const grade = tackling !== null ? await tackling.getScoreGrade(domain) : null;

            return new ScoreField(domain.scoreRange, grade?.score ?? null);
        }

        throw new Error(`unexpected grade domain ${domain}`);
    }

    getTackling() {
        if (this.user === null) return null;

        return new ObjectiveTackling(this.assignment, this.user, this.ctx);
    }
}
