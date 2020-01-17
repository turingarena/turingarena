import * as fs from 'fs';
import * as path from 'path';
import { BelongsTo, Column, ForeignKey, HasMany, HasOne, Model, PrimaryKey, Table, BelongsToMany } from 'sequelize-typescript';
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

    @BelongsToMany(() => File, () => SubmissionFile)
    files: File[];

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

    /**
     * Extract the files of this submission in the specified base dir.
     * It extract files as: `${base}/${file.fieldId}/${file.path}.
     *
     * @param base base directory
     */
    async extract(base: string) {
        // @ts-ignore
        const files = await this.getFiles();

        for (const file of files) {
            await file.extract(base);
        }
    }
}

/** File in a submission */
@Table({ timestamps: false })
export class SubmissionFile extends Model<SubmissionFile> {
    @ForeignKey(() => Submission)
    @PrimaryKey
    @Column
    submissionId!: number;

    @ForeignKey(() => File)
    @PrimaryKey
    @Column
    fileId!: number;
}
