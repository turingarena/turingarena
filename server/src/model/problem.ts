import * as fs from 'fs';
import * as path from 'path';
import { BelongsTo, BelongsToMany, Column, ForeignKey, HasMany, HasOne, Index, Model, PrimaryKey, Table, Unique } from 'sequelize-typescript';
import { ApiContext } from '../api';
import { Contest, ContestProblem } from './contest';
import { File } from './file';

/** A problem in TuringArena. */
@Table
export abstract class Problem extends Model<Problem> {
    /** Name of the problem, must be a valid identifier. */
    @Unique
    @Column
    @Index
    name!: string;

    /** Contests that contains this problem */
    @BelongsToMany(() => Contest, () => ContestProblem)
    contests: Contest[];

    /** Files that belongs to this problem. */
    @HasMany(() => ProblemFile)
    files: ProblemFile[];
    abstract getFiles(options: object): Promise<ProblemFile[]>;

    /**
     * Extract the files of this problem in the specified base dir.
     * The last updated timestamp of this problem is appended, and
     * nothing is done if the directory already exists.
     * Creates all the directories if they don't exist.
     *
     * @param base base directory
     */
    async extract(ctx: ApiContext, base: string) {
        const problemDir = path.join(base, this.updatedAt.getTime().toString());

        try {
            if ((await fs.promises.stat(problemDir)).isDirectory())
                return problemDir;
        } catch {
            // Directory doesn't exist and thus stat fails
        }

        const files = await this.getFiles({ include: [ctx.db.ProblemFile] });

        for (const file of files) {
            const filePath = path.join(base, file.path);
            console.debug('x', filePath);
            await file.file.extract(filePath);
        }

        return problemDir;
    }
}

/** Problem to File N-N relation. */
@Table({ timestamps: false })
export class ProblemFile extends Model<ProblemFile> {
    @PrimaryKey
    @ForeignKey(() => Problem)
    @Column({ unique: 'problem_path_unique' })
    problemId!: number;

    @PrimaryKey
    @ForeignKey(() => File)
    @Column
    fileId!: number;

    @Column({ unique: 'problem_path_unique' })
    path!: string;

    @BelongsTo(() => ProblemFile, 'problemId')
    problem: Problem;

    @HasOne(() => File, 'fileId')
    file: File;
}
