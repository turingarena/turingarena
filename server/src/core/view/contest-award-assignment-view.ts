import { gql } from 'apollo-server-core';
import { ApiObject } from '../../main/api';
import { ApiContext } from '../../main/api-context';
import { Resolvers } from '../../main/resolver-types';
import { typed } from '../../util/types';
import { ContestAwardAssignment } from '../contest-award-assignment';
import {
    ContestAwardAssignmentUserTackling,
    ContestAwardAssignmentUserTacklingApi,
} from '../contest-award-assignment-user-tackling';
import { FulfillmentField, FulfillmentGradeDomain } from '../feedback/fulfillment';
import { ScoreField, ScoreGradeDomain } from '../feedback/score';
import { User } from '../user';
import { ContestProblemAssignmentView } from './contest-problem-assignment-view';

export const contestAwardAssignmentViewSchema = gql`
    """
    Refers to a given award of a problem, assigned in a given contest, as seen by a given user or anonymously.
    """
    type ContestAwardAssignmentView {
        "Same award assigned in same contest."
        assignment: ContestAwardAssignment!
        "User viewing this, or null if anonymous."
        user: User
        "The problem containing the given award, assigned in same contest, as seen by same user or anonymously"
        problemAssignmentView: ContestProblemAssignmentView!

        "Current grade for this award in this contest, to show to the given user."
        gradeField: GradeField!
    }
`;

export class ContestAwardAssignmentView {
    constructor(readonly assignment: ContestAwardAssignment, readonly user: User | null) {}
    __typename = 'ContestAwardAssignmentView';
    async problemAssignmentView() {
        return typed<ContestProblemAssignmentView>({
            __typename: 'ContestProblemAssignmentView',
            assignment: this.assignment.problemAssignment,
            user: this.user,
        });
    }
    gradeField({}, ctx: ApiContext) {
        return ctx.api(ContestAwardAssignmentViewApi).getGradeField(this);
    }
}

export interface ContestAwardAssignmentViewModelRecord {
    ContestAwardAssignmentView: ContestAwardAssignmentView;
}

export class ContestAwardAssignmentViewApi extends ApiObject {
    getTackling({ assignment, user }: ContestAwardAssignmentView) {
        if (user === null) return null;

        return new ContestAwardAssignmentUserTackling(assignment, user);
    }

    async getGradeField(v: ContestAwardAssignmentView) {
        const { gradeDomain: domain } = v.assignment.award;
        const tackling = this.getTackling(v);

        if (domain instanceof FulfillmentGradeDomain) {
            const grade =
                tackling !== null
                    ? await this.ctx.api(ContestAwardAssignmentUserTacklingApi).getFulfillmentGrade(tackling)
                    : null;

            return new FulfillmentField(grade?.fulfilled ?? null);
        }

        if (domain instanceof ScoreGradeDomain) {
            const grade =
                tackling !== null
                    ? await this.ctx.api(ContestAwardAssignmentUserTacklingApi).getScoreGrade(tackling, domain)
                    : null;

            return new ScoreField(domain.scoreRange, grade?.score ?? null);
        }

        throw new Error(`unexpected grade domain ${domain}`);
    }
}

