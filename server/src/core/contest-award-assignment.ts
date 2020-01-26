import { gql } from 'apollo-server-core';
import { QueryTypes } from 'sequelize';
import { ResolversWithModels } from '../main/resolver-types';
import { Achievement } from './achievement';
import { ContestProblemAssignment } from './contest-problem-assignment';
import { Award } from './material/award';
import { User } from './user';

export const contestAwardAssignmentSchema = gql`
    type ContestAwardAssignment {
        problemAssignment: ContestProblemAssignment!
        award: Award!
    }
`;

export class ContestAwardAssignment {
    constructor(readonly problemAssignment: ContestProblemAssignment, readonly award: Award) {}

    async getBestAchievement(user: User) {
        const { sequelize, modelRoot } = this.problemAssignment;

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
                    problemId: this.problemAssignment.problemId,
                    userId: user.id,
                    awardIndex: this.award.index,
                },
                type: QueryTypes.SELECT,
                mapToModel: true,
                instance: modelRoot.table(Achievement).build(),
            },
        );

        return achievements.length > 0 ? achievements[0] : null;
    }
}

export const contestAwardAssignmentResolvers: ResolversWithModels<{
    ContestAwardAssignment: ContestAwardAssignment;
}> = {
    ContestAwardAssignment: {
        problemAssignment: ({ problemAssignment }) => problemAssignment,
        award: ({ award }) => award,
    },
};
