import { DataTypes } from 'sequelize';
import { AllowNull, Column, ForeignKey, Table } from 'sequelize-typescript';
import { ApiObject } from '../main/api';
import { UuidBaseModel } from '../main/base-model';
import { Achievement } from './achievement';
import { Evaluation } from './evaluation';

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
    async storeAchievements(e: EvaluationEvent) {
        if ('IOISubtaskScore' in e.data) {
            const { subtask, normalized_score, score } = e.data.IOISubtaskScore;
            await this.ctx.root.table(Achievement).create({
                evaluationId: e.evaluationId,
                awardIndex: subtask,
                // Store the normalized score if the max score is zero (FIXME: ugly hack)
                grade: score === 0 ? normalized_score : score,
            });
        }
    }
}

export type TaskMakerEvent =
    | TaskMakerIOISolutionEvent
    | TaskMakerIOISubtaskScoreEvent
    | TaskMakerIOITestCaseScoreEvent
    | TaskMakerCompilationEvent;

interface TaskMakerExecutionResult {
    status: string;
    was_killed: boolean;
    was_cached: boolean;
    resources: {
        cpu_time: number;
        sys_time: number;
        wall_time: number;
        memory: number;
    };
}

// FIXME: should this be an enum or union type?
interface TaskMakerStatus {
    Done?: {
        result: TaskMakerExecutionResult;
    };
}

interface TaskMakerIOISolutionEvent {
    IOIEvaluation: {
        subtask: number;
        testcase: number;
        solution: string;
        status: TaskMakerStatus;
    };
}

interface TaskMakerIOITestCaseScoreEvent {
    IOITestcaseScore: {
        subtask: number;
        testcase: number;
        solution: string;
        score: number;
        message: string;
    };
}

interface TaskMakerIOISubtaskScoreEvent {
    IOISubtaskScore: {
        subtask: number;
        solution: string;
        normalized_score: number;
        score: number;
    };
}

interface TaskMakerCompilationEvent {
    Compilation: {
        file: string;
        status: TaskMakerStatus;
    };
}
