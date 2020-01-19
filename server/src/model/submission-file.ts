import {
    AllowNull,
    BelongsTo,
    Column,
    ForeignKey,
    Model,
    PrimaryKey,
    Table,
} from 'sequelize-typescript';
import { File } from './file';
import { Submission } from './submission';

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
