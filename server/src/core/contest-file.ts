import { AllowNull, BelongsTo, Column, ForeignKey, PrimaryKey, Table } from 'sequelize-typescript';
import { BaseModel } from '../main/base-model';
import { Contest } from './contest';
import { FileContent } from './file-content';

/** Contest to File N-N relation */
@Table({ timestamps: false })
export class ContestFile extends BaseModel<ContestFile> {
    @ForeignKey(() => Contest)
    @PrimaryKey
    @Column
    contestId!: number;

    @ForeignKey(() => FileContent)
    @AllowNull(false)
    @Column
    fileId!: number;

    /** Path of this file in the contest, e.g. home.md */
    @PrimaryKey
    @Column
    path!: string;

    @BelongsTo(() => FileContent)
    file!: FileContent;

    @BelongsTo(() => Contest)
    contest!: Contest;
}
