import * as fs from 'fs';
import { DateTime } from 'luxon';
import * as mime from 'mime-types';
import * as path from 'path';
import { BelongsTo, Column, ForeignKey, HasMany, Index, Model, PrimaryKey, Table, Unique } from 'sequelize-typescript';
import { ApiContext } from '../api';
import { ContestProblem } from './contest';
import { File } from './file';

/** A problem in TuringArena. */
@Table
export class Problem extends Model<Problem> {
    /** Name of the problem, must be a valid identifier. */
    @Unique
    @Column
    @Index
    name!: string;

    /** Contests that contains this problem */
    @HasMany(() => ContestProblem)
    contestProblems: ContestProblem[];

    /** Files that belongs to this problem. */
    @HasMany(() => ProblemFile)
    problemFiles: ProblemFile[];
    getProblemFiles: (options: object) => Promise<ProblemFile[]>;
    createProblemFile: (problemFile: object, options: object) => Promise<ProblemFile>;

    /**
     * Extract the files of this problem in the specified base dir:
     * ${base}/${this.name}/${this.updatedAt}/<files...>
     * The last updated timestamp of this problem is appended, and
     * nothing is done if the directory already exists.
     * Creates all the directories if they don't exist.
     *
     * @param ctx Context to use
     * @param base Base directory
     */
    async extract(ctx: ApiContext, base: string) {
        const problemDir = path.join(base, this.name, DateTime.fromJSDate(this.updatedAt).toFormat('x--yyyy-MM-dd--hh-mm-ss'));

        try {
            if ((await fs.promises.stat(problemDir)).isDirectory())
                return problemDir;
        } catch {
            // Directory doesn't exist and thus stat fails
        }

        const problemFiles = await this.getProblemFiles({ include: [ctx.db.File] });

        for (const problemFile of problemFiles) {
            const filePath = path.join(problemDir, problemFile.path);
            await problemFile.file.extract(filePath);
        }

        return problemDir;
    }

    /**
     * Import the problem files from the filesystem
     *
     * @param ctx  Context to use
     * @param base Base directory to add
     * @param dir  Current directory
     */
    async addFiles(ctx, base: string, dir: string = '') {
        const files = fs.readdirSync(path.join(base, dir));
        for (const file of files) {
            const relPath = path.join(dir, file);
            if (fs.statSync(path.join(base, relPath)).isDirectory()) {
                await this.addFiles(ctx, base, relPath);
            } else {
                const content = fs.readFileSync(path.join(base, relPath));
                const type = mime.lookup(file);
                await this.createProblemFile(
                    {
                        path: relPath,
                        file: {
                            type: type !== false ? type : 'unknown',
                            content,
                        },
                    },
                    { include: [ctx.db.File] },
                );
            }
        }
    }

}

/** Problem to File N-N relation. */
@Table({ timestamps: false })
export class ProblemFile extends Model<ProblemFile> {
    @PrimaryKey
    @ForeignKey(() => Problem)
    @Column
    problemId!: number;

    @ForeignKey(() => File)
    @Column({ allowNull: false })
    fileId!: number;

    @PrimaryKey
    @Column
    path!: string;

    @BelongsTo(() => Problem)
    problem: Problem;

    @BelongsTo(() => File)
    file: File;
}
