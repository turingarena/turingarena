import { QueryTypes } from 'sequelize';
import { ApiContext } from '../main/api-context';
import { Achievement } from './achievement';
import { ObjectiveInstance } from './contest-objective-assignment';
import { FulfillmentGrade, FulfillmentGradeDomain } from './feedback/fulfillment';
import { ScoreGrade, ScoreGradeDomain } from './feedback/score';
import { User } from './user';

export class ObjectiveTackling {
    constructor(readonly instance: ObjectiveInstance, readonly user: User, readonly ctx: ApiContext) {}

    __typename = 'ObjectiveTackling' as const;

    async getBestAchievement() {
        const achievements = await this.ctx.db.query<Achievement>(
            `
                WITH
                    successful_evaluations AS (
                        SELECT e.*
                        FROM evaluations e
                    ),
                    official_evaluations AS (
                        SELECT e.*
                        FROM successful_evaluations e
                        WHERE e.id = (
                            SELECT e2.id
                            FROM successful_evaluations e2
                            WHERE e2.submission_id = e.submission_id
                            ORDER BY e2.created_at DESC
                            LIMIT 1
                        )
                    ),
                    submission_achievements AS (
                        SELECT a.*, s.id as submission_id, s.username, s.contest_id, s.problem_name, s.created_at
                        FROM achievements a
                                JOIN official_evaluations e ON a.evaluation_id = e.id
                                JOIN submissions s ON e.submission_id = s.id
                    ),
                    problem_achievements AS (
                        SELECT a.*
                        FROM submission_achievements a
                        WHERE a.submission_id = (
                            SELECT a2.submission_id
                            FROM submission_achievements a2
                            WHERE a2.username = a.username
                            AND a2.contest_id = a.contest_id
                            AND a2.problem_name = a.problem_name
                            AND a2.objective_index = a.objective_index
                            ORDER BY a2.grade DESC, a2.created_at
                            LIMIT 1
                        )
                    )
                SELECT *
                FROM problem_achievements
                WHERE username = $username
                    AND contest_id = $contestId
                    AND problem_name = $problemName
                    AND objective_index = $objectiveIndex;
            `,
            {
                bind: {
                    contestId: this.instance.problem.definition.contest.id,
                    problemName: this.instance.problem.definition.name,
                    username: this.user.username,
                    objectiveIndex: this.instance.definition.index,
                },
                type: QueryTypes.SELECT,
                mapToModel: true,
                instance: this.ctx.table(Achievement).build(),
            },
        );

        return achievements.length > 0 ? achievements[0] : null;
    }

    async getScoreGrade(domain: ScoreGradeDomain) {
        const bestAchievement = await this.getBestAchievement();

        return bestAchievement !== null ? bestAchievement.getScoreGrade(domain) : new ScoreGrade(domain.scoreRange, 0);
    }

    async getFulfillmentGrade() {
        const bestAchievement = await this.getBestAchievement();

        return bestAchievement !== null ? bestAchievement.getFulfillmentGrade() : new FulfillmentGrade(false);
    }

    async getGrade() {
        const { gradeDomain: domain } = this.instance.definition;
        if (domain instanceof FulfillmentGradeDomain) return (await this.getFulfillmentGrade()) ?? null;
        if (domain instanceof ScoreGradeDomain) return (await this.getScoreGrade(domain)) ?? null;
        throw new Error(`unexpected grade domain ${domain}`);
    }
}
