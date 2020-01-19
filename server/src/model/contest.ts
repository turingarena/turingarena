import * as fs from 'fs';
import * as path from 'path';
import {
    AllowNull,
    Column,
    HasMany,
    Index,
    Model,
    Table,
    Unique,
} from 'sequelize-typescript';
import { ApiContext } from '../api';
import { ContestFile } from './contest-file';
import { ContestProblem } from './contest-problem';
import { File } from './file';
import { Participation } from './participation';

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
