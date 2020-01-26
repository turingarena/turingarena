import { QueryTypes } from 'sequelize';
import { Achievement } from './achievement';
import { ContestAwardAssignment } from './contest-award-assignment';
import { FulfillmentDomain } from './feedback/fulfillment';
import { ScoreDomain } from './feedback/score';
import { User } from './user';

export class ContestAwardUserTackling {
    constructor(readonly assignment: ContestAwardAssignment, readonly user: User) {}

    async getBestAchievement() {
        const { sequelize, modelRoot } = this.assignment.problemAssignment;

        const achievements = await sequelize.query<Achievement>(
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
                        SELECT a.*, s.id as submission_id, s.user_id, s.problem_id, s.created_at
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
                            WHERE a2.user_id = a.user_id
                            AND a2.problem_id = a.problem_id
                            AND a2.award_index = a.award_index
                            ORDER BY a2.grade DESC, a2.created_at
                            LIMIT 1
                        )
                    )
                SELECT *
                FROM assignment_achievements
                WHERE user_id = $userId
                    AND problem_id = $problemId
                    AND award_index = $awardIndex;
            `,
            {
                bind: {
                    problemId: this.assignment.problemAssignment.problemId,
                    userId: this.user.id,
                    awardIndex: this.assignment.award.index,
                },
                type: QueryTypes.SELECT,
                mapToModel: true,
                instance: modelRoot.table(Achievement).build(),
            },
        );

        return achievements.length > 0 ? achievements[0] : null;
    }

    async getScoreValue(domain: ScoreDomain) {
        return (await this.getBestAchievement())?.getScoreValue(domain) ?? domain.zero();
    }

    async isFulfilled() {
        return (await this.getBestAchievement())?.isFulfilled() ?? false;
    }

    async getGrade() {
        const { gradeDomain: domain } = this.assignment.award;
        if (domain instanceof FulfillmentDomain) return (await this.isFulfilled()) ?? null;
        if (domain instanceof ScoreDomain) return (await this.getScoreValue(domain)) ?? null;
        throw new Error(`unexpected grade domain ${domain}`);
    }
}
