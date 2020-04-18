import { gql } from 'apollo-server-core';
import * as fs from 'fs';
import * as path from 'path';
import { AllowNull, Column, PrimaryKey, Table } from 'sequelize-typescript';
import * as ssri from 'ssri';
import { ApiObject } from '../../main/api';
import { BaseModel, createByIdDataLoader } from '../../main/base-model';
import { Resolvers } from '../../main/resolver-types';

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
export class FileContent extends BaseModel<FileContent> {
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

export interface FileContentModelRecord {
    FileContent: FileContent;
}

export class FileContentApi extends ApiObject {
    byId = createByIdDataLoader(this.ctx, FileContent);

    async createFromContent(content: Buffer) {
        const id = ssri.fromData(content).hexDigest();

        return (
            (await this.ctx.table(FileContent).findOne({ where: { id } })) ??
            (await this.ctx.table(FileContent).create({ content, id }))
        );
    }

    async createFromPath(filePath: string) {
        const content = fs.readFileSync(filePath);

        return this.createFromContent(content);
    }

    /**
     * Extract the file to path.
     * Creates necessary directories.
     *
     * @param path file path
     */
    async extract(fileContent: FileContent, filePath: string) {
        await fs.promises.mkdir(path.dirname(filePath), { recursive: true });

        return fs.promises.writeFile(filePath, fileContent.content);
    }
}

export const fileContentResolvers: Resolvers = {
    FileContent: {
        id: c => c.id,
        base64: c => c.content.toString('base64'),
        utf8: c => c.content.toString('utf8'),
    },
};
