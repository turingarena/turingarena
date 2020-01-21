import { gql } from 'apollo-server-core';
import * as fs from 'fs';
import * as mime from 'mime-types';
import * as path from 'path';
import { AllowNull, Column, DefaultScope, Index, Model, Scopes, Table, Unique } from 'sequelize-typescript';
import * as ssri from 'ssri';
import { ApiContext } from '../main/context';
import { ResolversWithModels } from '../main/resolver-types';

export const fileContentSchema = gql`
    type FileContent {
        hash: ID!

        base64: String!
        utf8: String!
    }

    input FileContentInput {
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
export class FileContent extends Model<FileContent> {
    /** The SHA-1 hash of the file. Is automatically computed on insert. */
    @Unique
    @AllowNull(false)
    @Index
    @Column
    hash!: string;

    /** MIME type of the file, e.g. text/plain, application/pdf, etc. */
    @AllowNull(false)
    @Column
    type!: string;

    /** Content in bytes of the file. */
    @AllowNull(false)
    @Column
    content!: Buffer;

    static async createFromContent(ctx: ApiContext, content: Buffer, type: string) {
        const hash = ssri.fromData(content).toString();

        return (
            (await ctx.table(FileContent).findOne({ where: { hash } })) ??
            (await ctx.table(FileContent).create({ content, type, hash }))
        );
    }

    static async createFromPath(ctx: ApiContext, filePath: string) {
        const content = fs.readFileSync(filePath);
        const lookup = mime.lookup(filePath);
        const type = lookup !== false ? lookup : 'unknown';

        return FileContent.createFromContent(ctx, content, type);
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
