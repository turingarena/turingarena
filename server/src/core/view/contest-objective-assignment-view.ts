import { gql } from 'apollo-server-core';
import { ApiContext } from '../../main/api-context';
import { ContestObjectiveAssignment } from '../contest-objective-assignment';
import { ContestObjectiveAssignmentUserTackling } from '../contest-objective-assignment-user-tackling';
import { FulfillmentField, FulfillmentGradeDomain } from '../feedback/fulfillment';
import { ScoreField, ScoreGradeDomain } from '../feedback/score';
import { User } from '../user';
import { ContestProblemAssignmentView } from './contest-problem-assignment-view';

export const contestObjectiveAssignmentViewSchema = gql`
    """
    Refers to a given objective of a problem, assigned in a given contest, as seen by a given user or anonymously.
    """
    type ContestObjectiveAssignmentView {
        "Same objective assigned in same contest."
        assignment: ContestObjectiveAssignment!
        "User viewing this, or null if anonymous."
        user: User
        "The problem containing the given objective, assigned in same contest, as seen by same user or anonymously"
        problemAssignmentView: ContestProblemAssignmentView!

        "Current grade for this objective in this contest, to show to the given user."
        gradeField: GradeField!
    }
`;

export class ContestObjectiveAssignmentView {
    constructor(readonly assignment: ContestObjectiveAssignment, readonly user: User | null, readonly ctx: ApiContext) {}

    __typename = 'ContestObjectiveAssignmentView' as const;

    async problemAssignmentView() {
        return new ContestProblemAssignmentView(this.assignment.problemAssignment, this.user, this.ctx);
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

        return new ContestObjectiveAssignmentUserTackling(this.assignment, this.user, this.ctx);
    }
}
