import { gql } from 'apollo-server-core';
import { AllowNull, BelongsTo, Column, ForeignKey, PrimaryKey, Table } from 'sequelize-typescript';
import { FindOptions } from 'sequelize/types';
import { ApiCache } from '../main/api-cache';
import { BaseModel, createSimpleLoader } from '../main/base-model';
import { FileContent } from './files/file-content';
import { SubmissionData } from './submission';

export const submissionFileSchema = gql`
    type SubmissionFile {
        contentId: ID!
        content: FileContent!
        fileName: String!
    }

    input SubmissionFileInput {
        fieldName: ID!
        fileTypeName: ID!
        fileName: String!
        content: FileContentInput!
    }
`;

/** File in a submission */
@Table({ timestamps: false })
export class SubmissionFile extends BaseModel<SubmissionFile> {
    @ForeignKey(() => SubmissionData)
    @PrimaryKey
    @Column
    submissionId!: number;

    @PrimaryKey
    @Column
    fieldName!: string;

    @Column
    fileTypeName!: string;

    @ForeignKey(() => FileContent)
    @AllowNull(false)
    @Column
    contentId!: string;

    @AllowNull(false)
    @Column
    fileName!: string;

    @BelongsTo(() => FileContent)
    content!: FileContent;
    getContent!: (options?: FindOptions) => Promise<FileContent>;
}

export class SubmissionFileCache extends ApiCache {
    bySubmission = createSimpleLoader((submissionId: string) =>
        this.ctx.table(SubmissionFile).findAll({ where: { submissionId } }),
    );
}
