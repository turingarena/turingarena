import { UIMessage } from '@edomora97/task-maker';
import { DataTypes } from 'sequelize';
import { AllowNull, Column, ForeignKey, Table } from 'sequelize-typescript';
import { ApiObject } from '../main/api';
import { ApiContext } from '../main/api-context';
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

    async storeAchievements(ctx: ApiContext) {
        if (typeof this.data === 'object' && 'IOISubtaskScore' in this.data) {
            const { subtask, normalized_score, score } = this.data.IOISubtaskScore;
            await ctx.table(Achievement).create({
                evaluationId: this.evaluationId,
                awardIndex: subtask,
                // Store the normalized score if the max score is zero (FIXME: ugly hack)
                grade: score === 0 ? normalized_score : score,
            });
        }
    }
}

export class EvaluationEventApi extends ApiObject {
    allByEvaluationId = createSimpleLoader((evaluationId: string) =>
        this.ctx.table(EvaluationEvent).findAll({
            where: { evaluationId },
        }),
    );
}
