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

    /** Path of the file, relative to something, e.g. sol/solution.cpp, home.md, etc. */
    @Column
    path!: string;

    /** Content in bytes of the file. */
    @Column
    content!: Buffer;

    static create(file) {
        const hash = createHash('sha1').update(file.content).digest('hex');

        // https://github.com/RobinBuschmann/sequelize-typescript/issues/291
        // tslint:disable-next-line: static-this
        return super.create.call(this, {
            content: file.content,
            fileName: file.fileName,
            type: file.type,
            hash,
        });
    }

    // tslint:disable-next-line: no-any
    static update(file): any {
        throw new Error('Modifying files is forbiddend!');
    }

    /**
     * Extract the path ${base}/${file.path}
     *
     * @param base base path
     */
    async extract(base: string) {
        const filePath = path.join(base, this.path);
        const dir = path.dirname(filePath);

        await fs.promises.mkdir(dir, { recursive: true });

        return fs.promises.writeFile(filePath, this.content);
    }
}
