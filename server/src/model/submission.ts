import * as path from 'path';
import {
    AllowNull,
    BelongsTo,
    Column,
    ForeignKey,
    HasMany,
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
    @AllowNull(false)
    @Column
    problemId!: number;

    @ForeignKey(() => Contest)
    @AllowNull(false)
    @Column
    contestId!: number;

    @ForeignKey(() => User)
    @AllowNull(false)
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
        const submissionFiles = await this.getSubmissionFiles();

        for (const submissionFile of submissionFiles) {
            const content = await submissionFile.getFile();
            const filePath = path.join(
                base,
                submissionFile.fieldId,
                submissionFile.fileName,
            );
            await content.extract(filePath);
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
    @AllowNull(false)
    @Column
    fileId!: number;

    @AllowNull(false)
    @Column
    fileName!: string;

    @BelongsTo(() => Submission)
    submission: Submission;

    @BelongsTo(() => File)
    file: File;
    getFile: () => Promise<File>;
}
