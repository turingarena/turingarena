import { DataTypes } from 'sequelize';
import { AllowNull, BelongsTo, Column, ForeignKey, Table } from 'sequelize-typescript';
import { BaseModel } from '../main/base-model';
import { Achievement } from './achievement';
import { Evaluation } from './evaluation';

/** Evant of an evaluation */
@Table({ updatedAt: false })
export class EvaluationEvent extends BaseModel<EvaluationEvent> {
    @ForeignKey(() => Evaluation)
    @AllowNull(false)
    @Column
    evaluationId!: number;

    /** Evaluation to which this event belongs to */
    @BelongsTo(() => Evaluation, 'evaluationId')
    evaluation!: Evaluation;

    /** Data of this event, in a backend-specific format */
    @AllowNull(false)
    @Column(DataTypes.JSON)
    data!: TaskMakerEvent;

    async storeAchievements() {
        if ('IOISubtaskScore' in this.data) {
            const { subtask, normalized_score, score } = this.data.IOISubtaskScore;
            await this.modelRoot.table(Achievement).create({
                evaluationId: this.evaluationId,
                subtaskIndex: subtask,
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
    Done: {
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
