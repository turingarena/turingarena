import { BelongsTo, Column, ForeignKey, HasMany, HasOne, Model, PrimaryKey, Table } from 'sequelize-typescript';
import { Contest } from './contest';
import { Evaluation } from './evaluation';
import { File } from './file';
import { Problem } from './problem';
import { User } from './user';

/** A Submission in the system */
@Table({ updatedAt: false })
export class Submission extends Model<Submission> {
    @ForeignKey(() => Problem)
    @Column
    problemId!: number;

    @ForeignKey(() => Contest)
    @Column
    contestId!: number;

    @ForeignKey(() => User)
    @Column
    userId!: number;

    /** Files that belongs to this submission */
    @HasMany(() => SubmissionFile)
    files: SubmissionFile[];

    /** Evaluations of this submission */
    @HasMany(() => Evaluation)
    evaluations: Evaluation[];

    /** Contest to which this submission belongs to */
    @BelongsTo(() => Contest, 'contestId')
    contest: Contest;

    /** Problem to which this submission is */
    @BelongsTo(() => Problem, 'problemId')
    problem: Problem;

    /** User that made this submission */
    @BelongsTo(() => User, 'userId')
    user: User;
}

/** File in a submission */
@Table({ timestamps: false })
export class SubmissionFile extends Model<SubmissionFile> {
    @ForeignKey(() => Submission)
    @PrimaryKey
    @Column
    submissionId!: number;

    @ForeignKey(() => File)
    @Column
    fileId!: number;

    /** Identifier of the field, e.g. solution */
    @PrimaryKey
    @Column
    fieldId!: string;

    /** Submission to which this file belongs to */
    @BelongsTo(() => Submission, 'submissionId')
    submission: Submission;

    /** File of this SubmissionFile */
    @HasOne(() => File, 'fileId')
    file: File;
}

