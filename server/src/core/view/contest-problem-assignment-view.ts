import { gql } from 'apollo-server-core';
import { ApiContext } from '../../main/api-context';
import { ObjectiveInstance } from '../contest-objective-assignment';
import { ProblemInstance } from '../contest-problem-assignment';
import { ProblemTackling } from '../contest-problem-assignment-user-tackling';
import { ProblemSetDefinition } from '../contest-problem-set';
import { ScoreField } from '../feedback/score';
import { ProblemMaterialCache } from '../material/problem-material';
import { User } from '../user';
import { ObjectiveView } from './contest-objective-assignment-view';
import { ProblemSetView } from './contest-problem-set-view';

export const problemViewSchema = gql`
    """
    Refers to a given problem, assigned in a given contest, as seen by a given user or anonymously.
    """
    type ProblemView {
        "Same problem assigned in same contest"
        assignment: ProblemInstance!
        "Viewing user, or null if anonymous"
        user: User

        "Set of problems in same contest, as seen by same user"
        problemSetView: ProblemSetView!

        """
        Same problem assigned in same contest tackled by same user,
        if the user is non-anonymous and allowed to have submissions for this problem in this contest,
        and null otherwise.
        """
        tackling: ProblemTackling

        "Current score seen by the user for this problem in this contest."
        totalScoreField: ScoreField!

        "Objectives of this problem assigned in same contest as seen by same user (or anonymously)"
        objectiveAssignmentViews: [ObjectiveView!]!
    }
`;

export class ProblemView {
    constructor(readonly assignment: ProblemInstance, readonly user: User | null, readonly ctx: ApiContext) {}

    __typename = 'ProblemView' as const;

    async problemSetView() {
        return new ProblemSetView(new ProblemSetDefinition(this.assignment.problem.contest), this.user, this.ctx);
    }

    async tackling() {
        return this.user !== null
            ? new ProblemTackling(this.assignment, this.user, this.ctx)
            : null;
    }

    async totalScoreField() {
        const { scoreRange } = await this.ctx.cache(ProblemMaterialCache).byId.load(this.assignment.problem.id());
        const tackling = await this.tackling();

        const scoreGrade = tackling !== null ? await tackling.scoreGrade() : null;

        return new ScoreField(scoreRange, scoreGrade?.score ?? null);
    }

    async objectiveAssignmentViews() {
        const { objectives } = await this.ctx.cache(ProblemMaterialCache).byId.load(this.assignment.problem.id());

        return objectives.map(
            objective =>
                new ObjectiveView(new ObjectiveInstance(this.assignment, objective), this.user, this.ctx),
        );
    }
}
