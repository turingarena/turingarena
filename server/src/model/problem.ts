import * as fs from 'fs';
import * as path from 'path';
import { BelongsToMany, Column, ForeignKey, Index, Model, PrimaryKey, Table, Unique } from 'sequelize-typescript';
import { Contest, ContestProblem } from './contest';
import { File } from './file';

/** Problem to File N-N relation. */
@Table({ timestamps: false })
export class ProblemFile extends Model<ProblemFile> {
    @PrimaryKey
    @ForeignKey(() => Problem)
    @Column
    problemId!: number;

    @PrimaryKey
    @ForeignKey(() => File)
    @Column
    fileId!: number;
}

/** A problem in TuringArena. */
@Table
export class Problem extends Model<Problem> {
    /** Name of the problem, must be a valid identifier. */
    @Unique
    @Column
    @Index
    name!: string;

    /** Contests that contains this problem */
    @BelongsToMany(() => Contest, () => ContestProblem)
    contests: Contest[];

    /** Files that belongs to this problem. */
    @BelongsToMany(() => File, () => ProblemFile)
    files: File[];

    /**
     * Extract the files of this problem in the specified base dir.
     * The last updated timestamp of this problem is appended, and
     * nothing is done if the directory already exists.
     * Creates all the directories if they don't exist.
     *
     * @param base base directory
     */
    async extract(base: string) {
        const problemDir = path.join(base, this.updatedAt.getTime().toString());

        try {
            if ((await fs.promises.stat(problemDir)).isDirectory())
                return;
        } catch {
            // Directory doesn't exist and thus stat fails
        }

        await fs.promises.mkdir(problemDir, { recursive: true });

        // @ts-ignore
        const files = await this.getFiles();

        for (const file of files) {
            await file.extract(problemDir);
        }
    }
}
