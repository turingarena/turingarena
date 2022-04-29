import { QueryTypes } from 'sequelize';
import { ApiContext } from '../main/api-context';
import { FulfillmentGrade, FulfillmentGradeDomain } from './data/fulfillment';
import { ScoreGrade, ScoreGradeDomain } from './data/score';
import { ObjectiveInstance } from './objective-instance';
import { OutcomeData } from './outcome';
import { User } from './user';

export class ObjectiveUndertaking {
    constructor(readonly instance: ObjectiveInstance, readonly user: User, readonly ctx: ApiContext) {}

    __typename = 'ObjectiveUndertaking' as const;

    async getBestOutcome() {
        const outcomes = await this.ctx.db.query<OutcomeData>(
            `
                SELECT *
                    FROM outcomes
                    WHERE user_id = $userId
                        AND problem_id = $problemId
                        AND objective_index = $objectiveIndex
                    ORDER BY grade DESC
                    LIMIT 1
                ;
            `,
            {
                bind: {
                    problemId: this.instance.problem.definition.id(),
                    userId: this.user.id,
                    objectiveIndex: this.instance.definition.index,
                },
                type: QueryTypes.SELECT,
                mapToModel: true,
                instance: this.ctx.table(OutcomeData).build(),
            },
        );

        return outcomes.length > 0 ? outcomes[0] : null;
    }

    async getScoreGrade(domain: ScoreGradeDomain) {
        const bestOutcome = await this.getBestOutcome();

        return bestOutcome !== null ? bestOutcome.getScoreGrade(domain) : new ScoreGrade(domain.scoreRange, 0);
    }

    async getFulfillmentGrade() {
        const bestOutcome = await this.getBestOutcome();

        return bestOutcome !== null ? bestOutcome.getFulfillmentGrade() : new FulfillmentGrade(false);
    }

    async getGrade() {
        const { gradeDomain: domain } = this.instance.definition;
        if (domain instanceof FulfillmentGradeDomain) return (await this.getFulfillmentGrade()) ?? null;
        if (domain instanceof ScoreGradeDomain) return (await this.getScoreGrade(domain)) ?? null;
        throw new Error(`unexpected grade domain ${domain}`);
    }
}
