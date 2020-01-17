import * as fs from 'fs';
import * as path from 'path';
import { BelongsToMany, Column, ForeignKey, Index, Model, PrimaryKey, Table, Unique, HasOne, BelongsTo, HasMany } from 'sequelize-typescript';
import { Contest, ContestProblem } from './contest';
import { File } from './file';
import { ApiContext } from '../api';


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
    @HasMany(() => ProblemFile)
    files: ProblemFile[];

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

        // @ts-ignore
        const files = await this.getFiles({ include: [ctx.db.ProblemFile] });

        for (const file of files) {
            const filePath = path.join(base, file.SubmissionFile.path);
            console.debug('x', filePath);
            await file.extract(filePath);
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
