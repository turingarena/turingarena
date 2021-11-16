import { gql } from 'apollo-server-core';
import { ApiContext } from '../../main/api-context';
import { ProblemSetDefinition } from '../contest-problem-set';
import { ProblemSetTackling } from '../contest-problem-set-user-tackling';
import { ScoreField } from '../feedback/score';
import { User } from '../user';
import { ProblemView } from './contest-problem-assignment-view';
import { ContestView } from './contest-view';

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
        contestView: ContestView!
        "The list of problems in the given problem-set, assigned in the same contest, as seen by the same user (or anonymously)."
        problems: [ProblemView!]!

        "Same contest as tackled by the same user, or null if anonymous."
        tackling: ProblemSetTackling

        "Current total score visible to the given user."
        totalScoreField: ScoreField!
    }
`;

export class ProblemSetView {
    constructor(readonly problemSet: ProblemSetDefinition, readonly user: User | null, readonly ctx: ApiContext) {}

    __typename = 'ProblemSetView' as const;

    contestView() {
        return new ContestView(this.problemSet.contest, this.user, this.ctx);
    }

    async problems() {
        return (await this.problemSet.contest.getProblems()).map(
            instance => new ProblemView(instance, this.user, this.ctx),
        );
    }

    tackling() {
        if (this.user === null) return null;

        return new ProblemSetTackling(this.problemSet, this.user, this.ctx);
    }

    async totalScoreField() {
        const tackling = this.tackling();

        const scoreRange = await this.problemSet.getScoreRange();
        const scoreGrade = tackling !== null ? await tackling.totalScoreGrade() : null;

        return new ScoreField(scoreRange, scoreGrade?.score ?? null);
    }
}
