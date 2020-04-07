import { gql } from 'apollo-server-core';
import * as fs from 'fs';
import * as path from 'path';
import { AllowNull, Column, Index, PrimaryKey, Table, Unique } from 'sequelize-typescript';
import * as ssri from 'ssri';
import { BaseModel } from '../main/base-model';
import { ModelRoot } from '../main/model-root';
import { Resolvers } from '../main/resolver-types';

export const fileContentSchema = gql`
    type FileContent {
        hash: ID!
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
    @Unique
    @PrimaryKey
    @AllowNull(false)
    @Index
    @Column
    hash!: string;

    /** Content in bytes of the file. */
    @AllowNull(false)
    @Column
    content!: Buffer;

    static async createFromContent(root: ModelRoot, content: Buffer) {
        const hash = ssri.fromData(content).hexDigest();

        return (
            (await root.table(FileContent).findOne({ where: { hash } })) ??
            (await root.table(FileContent).create({ content, hash }))
        );
    }

    static async createFromPath(root: ModelRoot, filePath: string) {
        const content = fs.readFileSync(filePath);

        return FileContent.createFromContent(root, content);
    }

    /**
     * Extract the file to path.
     * Creates necessary directories.
     *
     * @param path file path
     */
    async extract(filePath: string) {
        await fs.promises.mkdir(path.dirname(filePath), { recursive: true });

        return fs.promises.writeFile(filePath, this.content);
    }
}

export interface FileContentModelRecord {
    FileContent: FileContent;
}

export const fileContentResolvers: Resolvers = {
    FileContent: {
        base64: content => content.content.toString('base64'),
        utf8: content => content.content.toString('utf8'),
    },
};
