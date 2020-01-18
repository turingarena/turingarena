import * as fs from 'fs';
import * as path from 'path';
import {
    BelongsTo,
    BelongsToMany,
    Column,
    ForeignKey,
    HasMany,
    HasOne,
    Model,
    PrimaryKey,
    Table,
} from 'sequelize-typescript';
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

    /** Files of this submission */
    @HasMany(() => SubmissionFile)
    submissionFiles: SubmissionFile[];
    getSubmissionFiles: () => Promise<SubmissionFile[]>;

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
        const files = await this.getSubmissionFiles();

        for (const file of files) {
            const content = await file.getFile();
            console.log(`${base}/${file.fieldId}: ${content}`);
            await content.extract(`${base}/${file.fieldId}`);
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

    @PrimaryKey
    @Column
    fieldId!: string;

    @ForeignKey(() => File)
    @Column
    fileId!: number;

    @BelongsTo(() => Submission, 'submissionId')
    submission: Submission;

    @BelongsTo(() => File, 'fileId')
    file: File;
    getFile: () => Promise<File>;
}
