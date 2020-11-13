import { QueryTypes } from 'sequelize';
import { ApiObject } from '../main/api';
import { ApiContext } from '../main/api-context';
import { Achievement, AchievementApi } from './achievement';
import { ContestAwardAssignment } from './contest-award-assignment';
import { FulfillmentGrade, FulfillmentGradeDomain } from './feedback/fulfillment';
import { ScoreGrade, ScoreGradeDomain } from './feedback/score';
import { User } from './user';

export class ContestAwardAssignmentUserTackling {
    constructor(readonly assignment: ContestAwardAssignment, readonly user: User) {}

    __typename = 'ContestAwardAssignmentUserTackling';

    async getBestAchievement(ctx: ApiContext) {
        const achievements = await ctx.environment.sequelize.query<Achievement>(
            `
                WITH
                    successful_evaluations AS (
                        SELECT e.*
                        FROM evaluations e
                        WHERE e.status = 'SUCCESS'
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
                    assignment_achievements AS (
                        SELECT a.*
                        FROM submission_achievements a
                        WHERE a.submission_id = (
                            SELECT a2.submission_id
                            FROM submission_achievements a2
                            WHERE a2.username = a.username
                            AND a2.contest_id = a.contest_id
                            AND a2.problem_name = a.problem_name
                            AND a2.award_index = a.award_index
                            ORDER BY a2.grade DESC, a2.created_at
                            LIMIT 1
                        )
                    )
                SELECT *
                FROM assignment_achievements
                WHERE username = $username
                    AND contest_id = $contestId
                    AND problem_name = $problemName
                    AND award_index = $awardIndex;
            `,
            {
                bind: {
                    contestId: this.assignment.problemAssignment.problem.contest.id,
                    problemName: this.assignment.problemAssignment.problem.name,
                    username: this.user.username,
                    awardIndex: this.assignment.award.index,
                },
                type: QueryTypes.SELECT,
                mapToModel: true,
                instance: ctx.table(Achievement).build(),
            },
        );

        return achievements.length > 0 ? achievements[0] : null;
    }

    async getScoreGrade(ctx:ApiContext, domain: ScoreGradeDomain) {
        const bestAchievement = await this.getBestAchievement(ctx);

        return bestAchievement !== null
            ? ctx.api(AchievementApi).getScoreGrade(bestAchievement, domain)
            : new ScoreGrade(domain.scoreRange, 0);
    }

    async getFulfillmentGrade(ctx: ApiContext) {
        const bestAchievement = await this.getBestAchievement(ctx);

        return bestAchievement !== null
            ? ctx.api(AchievementApi).getFulfillmentGrade(bestAchievement)
            : new FulfillmentGrade(false);
    }

    async getGrade(ctx: ApiContext) {
        const { gradeDomain: domain } = this.assignment.award;
        if (domain instanceof FulfillmentGradeDomain) return (await this.getFulfillmentGrade(ctx)) ?? null;
        if (domain instanceof ScoreGradeDomain) return (await this.getScoreGrade(ctx, domain)) ?? null;
        throw new Error(`unexpected grade domain ${domain}`);
    }
}

export class ContestAwardAssignmentUserTacklingApi extends ApiObject {
    async getBestAchievement(t: ContestAwardAssignmentUserTackling) {
        const achievements = await this.ctx.environment.sequelize.query<Achievement>(
            `
                WITH
                    successful_evaluations AS (
                        SELECT e.*
                        FROM evaluations e
                        WHERE e.status = 'SUCCESS'
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
                    assignment_achievements AS (
                        SELECT a.*
                        FROM submission_achievements a
                        WHERE a.submission_id = (
                            SELECT a2.submission_id
                            FROM submission_achievements a2
                            WHERE a2.username = a.username
                            AND a2.contest_id = a.contest_id
                            AND a2.problem_name = a.problem_name
                            AND a2.award_index = a.award_index
                            ORDER BY a2.grade DESC, a2.created_at
                            LIMIT 1
                        )
                    )
                SELECT *
                FROM assignment_achievements
                WHERE username = $username
                    AND contest_id = $contestId
                    AND problem_name = $problemName
                    AND award_index = $awardIndex;
            `,
            {
                bind: {
                    contestId: t.assignment.problemAssignment.problem.contest.id,
                    problemName: t.assignment.problemAssignment.problem.name,
                    username: t.user.username,
                    awardIndex: t.assignment.award.index,
                },
                type: QueryTypes.SELECT,
                mapToModel: true,
                instance: this.ctx.table(Achievement).build(),
            },
        );

        return achievements.length > 0 ? achievements[0] : null;
    }

    async getScoreGrade(t: ContestAwardAssignmentUserTackling, domain: ScoreGradeDomain) {
        const bestAchievement = await this.getBestAchievement(t);

        return bestAchievement !== null
            ? this.ctx.api(AchievementApi).getScoreGrade(bestAchievement, domain)
            : new ScoreGrade(domain.scoreRange, 0);
    }

    async getFulfillmentGrade(t: ContestAwardAssignmentUserTackling) {
        const bestAchievement = await this.getBestAchievement(t);

        return bestAchievement !== null
            ? this.ctx.api(AchievementApi).getFulfillmentGrade(bestAchievement)
            : new FulfillmentGrade(false);
    }

    async getGrade(t: ContestAwardAssignmentUserTackling) {
        const { gradeDomain: domain } = t.assignment.award;
        if (domain instanceof FulfillmentGradeDomain) return (await this.getFulfillmentGrade(t)) ?? null;
        if (domain instanceof ScoreGradeDomain) return (await this.getScoreGrade(t, domain)) ?? null;
        throw new Error(`unexpected grade domain ${domain}`);
    }
}
