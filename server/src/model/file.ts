import { createHash } from 'crypto';
import * as fs from 'fs';
import * as path from 'path';
import { Column, Index, Model, Table, Unique } from 'sequelize-typescript';

/** A generic file in TuringArena. */
@Table({ updatedAt: false })
export class File extends Model<File> {
    /** The SHA-1 hash of the file. Is automatically computed on insert. */
    @Unique
    @Index
    @Column
    hash!: string;

    /** MIME type of the file, e.g. text/plain, application/pdf, etc. */
    @Column
    type!: string;

    /** Content in bytes of the file. */
    @Column
    content!: Buffer;

    static create(file) {
        const hash = createHash('sha1').update(file.content).digest('hex');

        // https://github.com/RobinBuschmann/sequelize-typescript/issues/291
        // tslint:disable: static-this
        try {
            return super.create.call(this, {
                content: file.content,
                fileName: file.fileName,
                type: file.type,
                hash,
            });
        } catch {
            // Probably already exists. Try to query it.
            return this.findOne({
                where: { hash },
            });
        }
    }

    // tslint:disable-next-line: no-any
    static update(file): any {
        throw new Error('Modifying files is forbiddend!');
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
