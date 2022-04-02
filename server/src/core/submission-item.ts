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
import { SubmissionFileType } from './problem-definition-file-types';
import { SubmissionField } from './problem-definition-material';
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
        readonly field: SubmissionField,
        readonly fileType: SubmissionFileType,
        readonly submission: Submission,
        readonly data: SubmissionItemData,
    ) {}

    private readonly contentType = mime.lookup(this.data.fileName);

    file = new File(
        `${this.field.name}.${this.fileType.name}${this.fileType.extension}`,
        null,
        this.contentType !== false ? this.contentType : `application/octet-stream`,
        new FileContent(this.data.fileContent),
        this.ctx,
    );
}

export class SubmissionItemCache extends ApiCache {
    bySubmission = createSimpleLoader(async (submissionId: string) => {
        const submission = new Submission(submissionId, this.ctx);
        const problemUndertaking = await submission.getUndertaking();
        const problemDefinition = problemUndertaking.instance.definition;
        const fields = await problemDefinition.submissionFields();
        const submissionFileTypeRules = await problemDefinition.submissionFileTypeRules();

        return Promise.all(
            fields.map(async field => {
                const itemData =
                    (await this.ctx
                        .table(SubmissionItemData)
                        .findOne({ where: { submissionId, fieldName: field.name } })) ??
                    unreachable(`submission is missing field '${field.name}'`);

                // TODO: type should be checked when submitting. Extract a function.
                const fileType =
                    submissionFileTypeRules
                        .map(
                            rule =>
                                rule.recommendedTypes.find(type => type.name === itemData.fileTypeName) ??
                                rule.otherTypes.find(type => type.name === itemData.fileTypeName) ??
                                null,
                        )
                        .find(x => x !== null) ?? unreachable(`submission field has invalid type`);

                return new SubmissionItem(this.ctx, field, fileType, submission, itemData);
            }),
        );
    });
}
