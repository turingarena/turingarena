import { UIMessage } from '@edomora97/task-maker';
import { DataTypes } from 'sequelize';
import { AllowNull, Column, ForeignKey, Table } from 'sequelize-typescript';
import { ApiObject } from '../main/api';
import { createSimpleLoader, UuidBaseModel } from '../main/base-model';
import { Achievement } from './achievement';
import { Evaluation } from './evaluation';

export type TaskMakerEvent = UIMessage;

/** Evant of an evaluation */
@Table({ updatedAt: false })
export class EvaluationEvent extends UuidBaseModel<EvaluationEvent> {
    @ForeignKey(() => Evaluation)
    @AllowNull(false)
    @Column
    evaluationId!: number;

    /** Data of this event, in a backend-specific format */
    @AllowNull(false)
    @Column(DataTypes.JSON)
    data!: TaskMakerEvent;
}

export class EvaluationEventApi extends ApiObject {
    allByEvaluationId = createSimpleLoader((evaluationId: string) =>
        this.ctx.table(EvaluationEvent).findAll({
            where: { evaluationId },
        }),
    );

    async storeAchievements(e: EvaluationEvent) {
        if (typeof e.data === 'object' && 'IOISubtaskScore' in e.data) {
            const { subtask, normalized_score, score } = e.data.IOISubtaskScore;
            await this.ctx.table(Achievement).create({
                evaluationId: e.evaluationId,
                awardIndex: subtask,
                // Store the normalized score if the max score is zero (FIXME: ugly hack)
                grade: score === 0 ? normalized_score : score,
            });
        }
    }
}
