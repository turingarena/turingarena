import { gql } from 'apollo-server-core';
import * as fs from 'fs';
import * as path from 'path';
import { AllowNull, Column, PrimaryKey, Table } from 'sequelize-typescript';
import * as ssri from 'ssri';
import { ApiCache } from '../../main/api-cache';
import { ApiContext } from '../../main/api-context';
import { BaseModel, createByIdDataLoader } from '../../main/base-model';
import { ApiOutputValue } from '../../main/graphql-types';

export const fileContentSchema = gql`
    type FileContent {
        id: ID!
        base64: String!
        utf8: String!
    }

    input FileContentInput {
        "Base64-encoded content of the file"
        base64: String!
    }
`;

export class FileContent implements ApiOutputValue<'FileContent'> {
    constructor(readonly data: Buffer) {}

    id = ssri.fromData(this.data).hexDigest();

    base64() {
        return this.data.toString('base64');
    }

    utf8() {
        return this.data.toString('utf8');
    }
}

/** A generic file in TuringArena. */
@Table({ updatedAt: false })
export class FileContentData extends BaseModel<FileContentData> {
    /** The SHA-1 hash of the file. Is automatically computed on insert. */
    @PrimaryKey
    @AllowNull(false)
    @Column
    id!: string;

    /** Content in bytes of the file. */
    @AllowNull(false)
    @Column
    content!: Buffer;
}

export class FileContentCache extends ApiCache {
    byId = createByIdDataLoader(this.ctx, FileContentData);
}

export async function createFileFromContent(ctx: ApiContext, data: Buffer) {
    const { id } = new FileContent(data);

    return (
        (await ctx.table(FileContentData).findOne({ where: { id } })) ??
        (await ctx.table(FileContentData).create({ content: data, id }))
    );
}

export async function createFileFromPath(ctx: ApiContext, filePath: string) {
    const content = fs.readFileSync(filePath);

    return createFileFromContent(ctx, content);
}

/**
 * Extract the file to path.
 * Creates necessary directories.
 *
 * @param path file path
 */
export async function extractFile(fileContent: FileContentData, filePath: string) {
    await fs.promises.mkdir(path.dirname(filePath), { recursive: true });

    return fs.promises.writeFile(filePath, fileContent.content);
}
