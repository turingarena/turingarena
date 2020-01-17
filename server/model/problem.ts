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
@BelongsToMany(() => Contest, () => ContestProblem)
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
}
