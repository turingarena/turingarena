import { gql } from 'apollo-server-core';
import { ApiContext } from '../main/api-context';
import { ContestView } from './contest-view';
import { ScoreField } from './data/score';
import { ProblemSetDefinition } from './problem-set-definition';
import { ProblemSetUndertaking } from './problem-set-undertaking';
import { ProblemView } from './problem-view';
import { User } from './user';

export const problemSetViewSchema = gql`
    """
    The problem-set of a given contest, as seen by a given user or anonymously.
    """
    type ProblemSetView {
        "The problem-set of the same contest."
        problemSet: ProblemSetDefinition!
        "The given user, if any, or null if anonymous."
        user: User
        "Same contest, as seen by the same user (or anonymously)."
        contest: ContestView!
        "The list of problems in the given problem-set, assigned in the same contest, as seen by the same user (or anonymously)."
        problems: [ProblemView!]!

        "Same contest as tackled by the same user, or null if anonymous."
        undertaking: ProblemSetUndertaking

        "Current total score visible to the given user."
        totalScoreField: ScoreField!
    }
`;

export class ProblemSetView {
    constructor(readonly problemSet: ProblemSetDefinition, readonly user: User | null, readonly ctx: ApiContext) {}

    __typename = 'ProblemSetView' as const;

    contest() {
        return new ContestView(this.problemSet.contest, this.user, this.ctx);
    }

    async problems() {
        return (await this.problemSet.contest.getProblems()).map(
            instance => new ProblemView(instance, this.user, this.ctx),
        );
    }

    undertaking() {
        if (this.user === null) return null;

        return new ProblemSetUndertaking(this.problemSet, this.user, this.ctx);
    }

    async totalScoreField() {
        const undertaking = this.undertaking();

        const scoreRange = await this.problemSet.getScoreRange();
        const scoreGrade = undertaking !== null ? await undertaking.totalScoreGrade() : null;

        return new ScoreField(scoreRange, scoreGrade?.score ?? null);
    }
}
