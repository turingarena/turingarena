import * as fs from 'fs';
import * as path from 'path';
import {
    AllowNull,
    BelongsTo,
    Column,
    ForeignKey,
    HasMany,
    Index,
    Model,
    PrimaryKey,
    Table,
    Unique,
} from 'sequelize-typescript';
import { ApiContext } from '../api';
import { File } from './file';
import { Problem } from './problem';
import { User } from './user';

/** A contest in TuringArena */
@Table
export class Contest extends Model<Contest> {
    /** Name of the contest, must be a valid identifier, e.g. ioi */
    @Unique
    @Index
    @AllowNull(false)
    @Column
    name!: string;

    /** Title of the contest, as a string, e.g. 'International Olimpics in Informatics' */
    @AllowNull(false)
    @Column
    title!: string;

    /** When the contest will start */
    @AllowNull(false)
    @Column
    start!: Date;

    /** When the contest will end */
    @AllowNull(false)
    @Column
    end!: Date;

    /** The list of problems in this contest */
    @HasMany(() => ContestProblem)
    contestProblems: ContestProblem[];
    createContestProblem: (
        contestProblem: object,
        options?: object,
    ) => Promise<ContestProblem>;

    /** The list of users in this contest */
    @HasMany(() => Participation)
    participations: Participation[];
    getParticipations: (options: object) => Promise<Participation[]>;
    createParticipation: (
        participation: object,
        options: object,
    ) => Promise<Participation>;

    /** The list of files in this contest */
    @HasMany(() => ContestFile)
    contestFiles: ContestFile[];
    getContestFiles: (options: object) => Promise<ContestFile[]>;
    createContestFile: (
        contestFile: object,
        options?: object,
    ) => Promise<ContestFile>;

    /**
     * Add files to this contest
     *
     * @param ctx  Context of the database
     * @param base Base directory to add
     * @param dir  Relative directory in recursive call
     */
    async addFiles(ctx: ApiContext, base: string, dir: string = '') {
        const files = fs.readdirSync(path.join(base, dir));
        for (const file of files) {
            const relPath = path.join(dir, file);
            if (fs.statSync(path.join(base, relPath)).isDirectory())
                await this.addFiles(ctx, base, relPath);
            else {
                const fileRow = await File.createFromPath(
                    ctx,
                    path.join(base, relPath),
                );
                await this.createContestFile({
                    path: relPath,
                    fileId: fileRow.id,
                });
            }
        }
    }
}

/** Contest to File N-N relation */
@Table({ timestamps: false })
export class ContestFile extends Model<ContestFile> {
    @ForeignKey(() => Contest)
    @PrimaryKey
    @Column
    contestId!: number;

    @ForeignKey(() => File)
    @AllowNull(false)
    @Column
    fileId!: number;

    /** Path of this file in the contest, e.g. home.md */
    @PrimaryKey
    @Column
    path!: string;

    @BelongsTo(() => File)
    file: File;

    @BelongsTo(() => Contest)
    contest: Contest;
}

/** User participation relation */
@Table({ timestamps: false })
export class Participation extends Model<Participation> {
    @ForeignKey(() => User)
    @PrimaryKey
    @Column
    userId!: number;

    @ForeignKey(() => Contest)
    @PrimaryKey
    @Column
    contestId!: number;

    @BelongsTo(() => Contest)
    contest: Contest;

    @BelongsTo(() => User)
    user: User;
}

/** Contest to Problem N-N relation */
@Table({ timestamps: false })
export class ContestProblem extends Model<ContestProblem> {
    @ForeignKey(() => Problem)
    @PrimaryKey
    @Column
    problemId!: number;

    @ForeignKey(() => Contest)
    @PrimaryKey
    @Column
    contestId!: number;

    @BelongsTo(() => Contest)
    contest: Contest;

    @BelongsTo(() => Problem)
    problem: Problem;
}
