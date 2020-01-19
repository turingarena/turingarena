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
import { Problem } from './problem';

/** Problem to File N-N relation. */
@Table({ timestamps: false })
export class ProblemFile extends Model<ProblemFile> {
    @ForeignKey(() => Problem)
    @PrimaryKey
    @Column
    problemId!: number;

    @ForeignKey(() => File)
    @AllowNull(false)
    @Column
    fileId!: number;

    @PrimaryKey
    @Column
    path!: string;

    @BelongsTo(() => Problem)
    problem: Problem;

    @BelongsTo(() => File)
    file: File;
    getFile: (options?: object) => Promise<File>;
}
