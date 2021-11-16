import { gql } from 'apollo-server-core';
import { ApiContext } from '../main/api-context';
import { ApiOutputValue } from '../main/graphql-types';
import { Contest } from './contest';
import { ScoreRange } from './data/score';
import { ProblemSetUndertaking } from './problem-set-undertaking';

export const problemSetSchema = gql`
    """
    Collection of problems in a contest.
    """
    type ProblemSetDefinition {
        """
        Contest containing this problem set.
        """
        contest: Contest!

        """
        Items in this problem set.
        Each corresponds to a problem assigned in the contest.
        """
        problems: [ProblemInstance!]!

        # TODO: grade domain
        undertakings: [ProblemSetUndertaking!]!
    }
`;

export class ProblemSetDefinition implements ApiOutputValue<'ProblemSetDefinition'> {
    readonly ctx: ApiContext;
    constructor(readonly contest: Contest) {
        this.ctx = contest.ctx;
    }

    __typename = 'ProblemSetDefinition' as const;

    async problems() {
        return this.contest.getProblems();
    }

    async undertakings(): Promise<ProblemSetUndertaking[]> {
        await this.ctx.authorizeAdmin();

        const users = await this.contest.getParticipatingUsers();
        return users.map(user => new ProblemSetUndertaking(this, user, this.ctx));
    }

    async getScoreRange(): Promise<ScoreRange> {
        const material = await this.contest.getProblemSetMaterial();

        return ScoreRange.total(material.map(m => m.scoreRange));
    }
}
