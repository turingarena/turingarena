import { gql } from 'apollo-server-core';
import { ApiContext } from '../main/api-context';
import { ProblemTackling } from './problem-tackling';
import { ProblemSetDefinition } from './problem-set-definition';
import { ScoreGrade } from './feedback/score';
import { User } from './user';
import { ProblemSetView } from './problem-set-view';

export const problemSetTacklingSchema = gql`
    """
    The problem set of a given contest, tackled by a given user.
    """
    type ProblemSetTackling {
        "The problem set."
        definition: ProblemSetDefinition!
        "The given user."
        user: User!

        "Same problem-set seen by same user."
        view: ProblemSetView!

        problems: [ProblemTackling!]!

        totalScoreGrade: ScoreGrade!
    }
`;

export class ProblemSetTackling {
    constructor(readonly definition: ProblemSetDefinition, readonly user: User, readonly ctx: ApiContext) {}

    __typename = 'ProblemSetTackling' as const;

    view() {
        return new ProblemSetView(this.definition, this.user, this.ctx);
    }

    async totalScoreGrade() {
        const problems = await this.definition.contest.getProblems();

        return ScoreGrade.total(
            await Promise.all(
                problems.map(async problem => new ProblemTackling(problem, this.user, this.ctx).totalScoreGrade()),
            ),
        );
    }

    async problems() {
        const problems = await this.definition.contest.getProblems();

        return problems.map(problem => new ProblemTackling(problem, this.user, this.ctx));
    }
}
