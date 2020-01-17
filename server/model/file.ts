import { createHash } from 'crypto';
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
        return super.create.call(this, {
            content: file.content,
            fileName: file.fileName,
            type: file.type,
            hash,
        });
    }

    static update(file): any {
        throw new Error('Modifying files is forbiddend!');
    }
}

