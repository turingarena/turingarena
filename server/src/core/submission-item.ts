import { gql } from 'apollo-server-core';
import * as mime from 'mime-types';
import { AllowNull, Column, ForeignKey, PrimaryKey, Table } from 'sequelize-typescript';
import { ApiCache } from '../main/api-cache';
import { ApiContext } from '../main/api-context';
import { BaseModel, createSimpleLoader } from '../main/base-model';
import { ApiOutputValue } from '../main/graphql-types';
import { unreachable } from '../util/unreachable';
import { File } from './data/file';
import { FileContent } from './files/file-content';
import { submissionFileTypes } from './problem-definition-file-types';
import { Submission, SubmissionData } from './submission';

export const submissionFileSchema = gql`
    type SubmissionItem {
        submission: Submission!
        field: SubmissionField!
        file: File!
        fileType: SubmissionFileType!
    }

    input SubmissionFileInput {
        fieldName: ID!
        fileTypeName: ID!
        fileName: String!
        content: FileContentInput!
    }
`;

/** File in a submission */
@Table({ timestamps: false, tableName: 'submission_files' })
export class SubmissionItemData extends BaseModel<SubmissionItemData> {
    @ForeignKey(() => SubmissionData)
    @PrimaryKey
    @Column
    submissionId!: number;

    @PrimaryKey
    @Column
    fieldName!: string;

    @Column
    fileTypeName!: string;

    @AllowNull(false)
    @Column
    fileName!: string;

    @AllowNull(false)
    @Column
    fileContent!: Buffer;
}

export class SubmissionItem implements ApiOutputValue<'SubmissionItem'> {
    constructor(
        readonly ctx: ApiContext,
        readonly field: ApiOutputValue<'SubmissionField'>,
        readonly submission: Submission,
        readonly data: SubmissionItemData,
    ) {}

    private readonly contentType = mime.lookup(this.data.fileName);

    // FIXME: file name should be sanitized or constant (e.g. `submission-NUM-solution.py`)
    file = new File(
        this.data.fileName,
        null,
        this.contentType !== false ? this.contentType : `application/octet-stream`,
        new FileContent(this.data.fileContent),
        this.ctx,
    );

    fileType =
        submissionFileTypes.find(x => x.name === this.data.fileTypeName) ?? unreachable(`invalid submission item type`);
}

export class SubmissionItemCache extends ApiCache {
    bySubmission = createSimpleLoader(async (submissionId: string) => {
        const submission = new Submission(submissionId, this.ctx);
        const problemUndertaking = await submission.getUndertaking();
        const fields = await problemUndertaking.instance.definition.submissionFields();

        return Promise.all(
            fields.map(async field => {
                const itemData = await this.ctx
                    .table(SubmissionItemData)
                    .findOne({ where: { submissionId, fieldName: field.name } });

                return new SubmissionItem(
                    this.ctx,
                    field,
                    submission,
                    itemData ?? unreachable(`submission is missing field '${field.name}'`),
                );
            }),
        );
    });
}
