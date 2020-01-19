import {
    AllowNull,
    BelongsTo,
    Column,
    ForeignKey,
    Model,
    PrimaryKey,
    Table,
} from 'sequelize-typescript';
import { Contest } from './contest';
import { File } from './file';

/** Contest to File N-N relation */
@Table({ timestamps: false })
export class ContestFile extends Model<ContestFile> {
    @ForeignKey(() => Contest)
    @PrimaryKey
    @Column
    contestId!: number;

    @ForeignKey(() => File)
    @AllowNull(false)
    @Column
    fileId!: number;

    /** Path of this file in the contest, e.g. home.md */
    @PrimaryKey
    @Column
    path!: string;

    @BelongsTo(() => File)
    file: File;

    @BelongsTo(() => Contest)
    contest: Contest;
}
