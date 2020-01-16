import {
    AutoIncrement,
    BelongsToMany,
    Column,
    ForeignKey,
    HasMany,
    Model,
    PrimaryKey,
    Table
} from 'sequelize-typescript';
import { Contest } from './contest';
import { File } from './file';
import { Problem } from './problem';
import { User } from './user';

@Table({ timestamps: false })
export class SubmissionFile extends Model<SubmissionFile> {
    @ForeignKey(() => Submission)
    @PrimaryKey
    @Column
    submissionId!: number;

    @ForeignKey(() => File)
    @Column
    fileId!: number;

    @PrimaryKey
    @Column
    fieldId!: string;

    @Column
    type!: string;
}

@Table
export class Submission extends Model<Submission> {
    @PrimaryKey
    @AutoIncrement
    @Column
    id!: number;

    @ForeignKey(() => Problem)
    @Column
    problemId!: number;

    @ForeignKey(() => Contest)
    @Column
    contestId!: number;

    @ForeignKey(() => User)
    @Column
    userId!: number;

    @BelongsToMany(() => File, () => SubmissionFile)
    files: File[];

    @HasMany(() => Evaluation)
    evaluations: Evaluation[];
}

@Table
export class Evaluation extends Model<Evaluation> {
    @PrimaryKey
    @AutoIncrement
    @Column
    id!: number;

    @ForeignKey(() => Submission)
    @Column
    submissionId!: number;
}

@Table
export class EvaluationEvent extends Model<EvaluationEvent> {
    @ForeignKey(() => Evaluation)
    @PrimaryKey
    @Column
    evaluationId!: number;

    @PrimaryKey
    @Column
    createdAt!: Date;

    @Column
    data!: string;
}
