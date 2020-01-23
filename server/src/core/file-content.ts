import { gql } from 'apollo-server-core';
import * as fs from 'fs';
import * as path from 'path';
import { AllowNull, Column, DefaultScope, Index, Scopes, Table, Unique } from 'sequelize-typescript';
import * as ssri from 'ssri';
import { BaseModel } from '../main/base-model';
import { ModelRoot } from '../main/model-root';
import { ResolversWithModels } from '../main/resolver-types';

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
@DefaultScope(() => ({
    attributes: ['id', 'hash', 'type'],
}))
@Scopes(() => ({
    withData: {
        attributes: ['id', 'hash', 'type', 'content'],
    },
}))
@Table({ updatedAt: false })
export class FileContent extends BaseModel<FileContent> {
    /** The SHA-1 hash of the file. Is automatically computed on insert. */
    @Unique
    @AllowNull(false)
    @Index
    @Column
    hash!: string;

    /** Content in bytes of the file. */
    @AllowNull(false)
    @Column
    content!: Buffer;

    static async createFromContent(root: ModelRoot, content: Buffer) {
        const hash = ssri.fromData(content).toString();

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

export const fileContentResolvers: ResolversWithModels<{
    FileContent: FileContent;
}> = {
    FileContent: {
        base64: async content => (await content.reload({ attributes: ['id', 'content'] })).content.toString('base64'),
        utf8: async content => (await content.reload({ attributes: ['id', 'content'] })).content.toString('utf8'),
    },
};
