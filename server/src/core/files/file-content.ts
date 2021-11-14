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

/** A generic file in TuringArena. */
@Table({ updatedAt: false })
export class FileContent extends BaseModel<FileContent> implements ApiOutputValue<'FileContent'> {
    /** The SHA-1 hash of the file. Is automatically computed on insert. */
    @PrimaryKey
    @AllowNull(false)
    @Column
    id!: string;

    /** Content in bytes of the file. */
    @AllowNull(false)
    @Column
    content!: Buffer;

    base64() {
        return this.content.toString('base64');
    }
    utf8() {
        return this.content.toString('utf8');
    }
}

export class FileContentCache extends ApiCache {
    byId = createByIdDataLoader(this.ctx, FileContent);
}

export async function createFileFromContent(ctx: ApiContext, content: Buffer) {
    const id = ssri.fromData(content).hexDigest();

    return (
        (await ctx.table(FileContent).findOne({ where: { id } })) ??
        (await ctx.table(FileContent).create({ content, id }))
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
export async function extractFile(fileContent: FileContent, filePath: string) {
    await fs.promises.mkdir(path.dirname(filePath), { recursive: true });

    return fs.promises.writeFile(filePath, fileContent.content);
}
