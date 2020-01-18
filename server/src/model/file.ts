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
import { ApiContext } from '../api';

/** A generic file in TuringArena. */
@Table({ updatedAt: false })
export class File extends Model<File> {
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
        fileContent: Buffer,
        contentType: string,
    ) {
        const hash = createHash('sha1')
            .update(fileContent)
            .digest('hex');

        return (
            (await ctx.db.File.findOne({ where: { hash } })) ??
            (await ctx.db.File.create({
                content: fileContent,
                type: contentType,
                hash,
            }))
        );
    }

    static async createFromPath(ctx: ApiContext, filePath: string) {
        const content = fs.readFileSync(filePath);
        const lookup = mime.lookup(filePath);
        const type = lookup !== false ? lookup : 'unknown';

        return File.createFromContent(ctx, content, type);
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
