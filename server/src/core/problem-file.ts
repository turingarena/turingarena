import {
    AllowNull,
    BelongsTo,
    Column,
    ForeignKey,
    Model,
    PrimaryKey,
    Table,
} from 'sequelize-typescript';
import { FileContent } from './file-content';
import { Problem } from './problem';

/** Problem to File N-N relation. */
@Table({ timestamps: false })
export class ProblemFile extends Model<ProblemFile> {
    @ForeignKey(() => Problem)
    @PrimaryKey
    @Column
    problemId!: number;

    @ForeignKey(() => FileContent)
    @AllowNull(false)
    @Column
    fileId!: number;

    @PrimaryKey
    @Column
    path!: string;

    @BelongsTo(() => Problem)
    problem: Problem;

    @BelongsTo(() => FileContent)
    file: FileContent;
    getFile: (options?: object) => Promise<FileContent>;
}
