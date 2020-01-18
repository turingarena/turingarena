import * as fs from 'fs';
import { DateTime } from 'luxon';
import * as mime from 'mime-types';
import * as path from 'path';
import { AllowNull, BelongsTo, Column, ForeignKey, HasMany, Index, Model, PrimaryKey, Table, Unique } from 'sequelize-typescript';
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
    findProblemFile: (options: object) => Promise<ProblemFile>;
    createProblemFile: (problemFile: object, options?: object) => Promise<ProblemFile>;

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
                const fileRow = await File.createFromPath(ctx, path.join(base, relPath));
                await this.createProblemFile({
                    path: relPath,
                    fileId: fileRow.id,
                });
            }
        }
    }

    async metadata(ctx: ApiContext): Promise<ProblemMetadata> {
        const metadataProblemFile = await ctx.db.ProblemFile.findOne({
            where: {
                problemId: this.id,
                path: '.task-info.json',
            },
        });

        const metadataFile = await metadataProblemFile.getFile();

        return JSON.parse(metadataFile.content.toString());
    }
}

/** Problem to File N-N relation. */
@Table({ timestamps: false })
export class ProblemFile extends Model<ProblemFile> {
    @ForeignKey(() => Problem)
    @PrimaryKey
    @Column
    problemId!: number;

    @ForeignKey(() => File)
    @AllowNull(false)
    @Column
    fileId!: number;

    @PrimaryKey
    @Column
    path!: string;

    @BelongsTo(() => Problem)
    problem: Problem;

    @BelongsTo(() => File)
    file: File;
    getFile: (options?: object) => Promise<File>;
}

/** Generic problem metadata */
interface ProblemMetadata {
    version: number;
    task_type: string;
    name: string;
    title: string;
    limits: {
        time: number;
        memory: number;
    };
    scoring: {
        max_score: number;
        subtasks: Array<{
            max_score: number;
            testcases: number;
        }>;
    };
    statements: Array<{
        language: string;
        content_type: string;
        path: string;
    }>;
    attachments: Array<{
        name: string;
        content_type: string;
        path: string;
    }>;
}
