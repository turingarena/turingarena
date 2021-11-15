import { gql } from 'apollo-server-core';
import { ApiOutputValue } from '../../main/graphql-types';
import { FulfillmentGradeDomain } from '../feedback/fulfillment';
import { ScoreGradeDomain, ScoreRange } from '../feedback/score';
import { ProblemMaterial } from './problem-material';
import { Text } from './text';

export const objectiveSchema = gql`
    """
    Graded element in a problem.
    For every objective of a problem, a progressively higher grade can be achieved during a contest.
    Corresponds to a subtask in IOI-like problems (assuming max-by-subtask scoring strategy).
    """
    type Objective {
        id: ID!

        problem: Problem!

        "Name used to identify this objective in this problem. Only for admins."
        name: String!
        "Name of this objective to display to users."
        title: Text!
        "Possible grades that can be achieved for this objective"
        gradeDomain: GradeDomain!
    }
`;

export class Objective implements ApiOutputValue<'Objective'> {
    constructor(readonly material: ProblemMaterial, readonly index: number) {}

    private readonly subtaskInfo = this.material.taskInfo.IOI.scoring.subtasks[this.index];

    name = `subtask.${this.index}`;
    title = new Text([{ value: `Subtask ${this.index}` }]);

    gradeDomain =
        this.subtaskInfo.max_score > 0
            ? new ScoreGradeDomain(new ScoreRange(this.subtaskInfo.max_score, 0, true))
            : new FulfillmentGradeDomain();

    id() {
        return `${this.material.problem.contest.id}/${this.material.problem.name}/${this.index}`;
    }
    problem() {
        return this.material.problem;
    }
}