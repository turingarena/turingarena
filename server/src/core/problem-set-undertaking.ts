import { gql } from 'apollo-server-core';
import { ApiContext } from '../main/api-context';
import { ScoreGrade } from './data/score';
import { ProblemSetDefinition } from './problem-set-definition';
import { ProblemSetView } from './problem-set-view';
import { ProblemUndertaking } from './problem-undertaking';
import { User } from './user';

export const problemSetUndertakingSchema = gql`
    """
    The problem set of a given contest, tackled by a given user.
    """
    type ProblemSetUndertaking {
        "The problem set."
        definition: ProblemSetDefinition!
        "The given user."
        user: User!

        "Same problem-set seen by same user."
        view: ProblemSetView!

        problems: [ProblemUndertaking!]!

        totalScoreGrade: ScoreGrade!
    }
`;

export class ProblemSetUndertaking {
    constructor(readonly definition: ProblemSetDefinition, readonly user: User, readonly ctx: ApiContext) {}

    __typename = 'ProblemSetUndertaking' as const;

    view() {
        return new ProblemSetView(this.definition, this.user, this.ctx);
    }

    async totalScoreGrade() {
        const problems = await this.definition.contest.getProblems();

        return ScoreGrade.total(
            await Promise.all(
                problems.map(async problem => new ProblemUndertaking(problem, this.user, this.ctx).totalScoreGrade()),
            ),
        );
    }

    async problems() {
        const problems = await this.definition.contest.getProblems();

        return problems.map(problem => new ProblemUndertaking(problem, this.user, this.ctx));
    }
}
