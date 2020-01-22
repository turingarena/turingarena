import { gql } from 'apollo-server-core';
import { AllowNull, BelongsTo, Column, ForeignKey, PrimaryKey, Table } from 'sequelize-typescript';
import { BaseModel } from '../main/base-model';
import { FileContent } from './file-content';
import { Submission } from './submission';

export const submissionFileSchema = gql`
    type SubmissionFile {
        fieldId: ID!
        content: FileContent!
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
    @ForeignKey(() => Submission)
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
    contentId!: number;

    @AllowNull(false)
    @Column
    fileName!: string;

    @BelongsTo(() => Submission)
    submission!: Submission;

    @BelongsTo(() => FileContent)
    content!: FileContent;
    getContent!: () => Promise<FileContent>;
}
