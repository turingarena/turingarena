import { gql } from 'apollo-server-core';
import { createHash } from 'crypto';
import * as fs from 'fs';
import * as mime from 'mime-types';
import * as path from 'path';
import {
    AllowNull,
    Column,
    Index,
    Model,
    Table,
    Unique,
} from 'sequelize-typescript';
import { Resolvers } from '../generated/graphql-types';
import { ApiContext } from '../main/context';

export const fileSchema = gql`
    type FileContent {
        hash: ID!
        base64: String!
    }

    input FileInput {
        contentBase64: String!
    }
`;

/** A generic file in TuringArena. */
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

    static async createFromContent(
        ctx: ApiContext,
        content: Buffer,
        type: string,
    ) {
        const hash = createHash('sha1')
            .update(content)
            .digest('hex');

        return (
            (await ctx.db.FileContent.findOne({ where: { hash } })) ??
            (await ctx.db.FileContent.create({ content, type, hash }))
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

export const fileContentResolvers: Resolvers = {
    FileContent: {
        base64: content => content.content.toString('base64'),
    },
};
