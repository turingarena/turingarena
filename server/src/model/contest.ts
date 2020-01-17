import { gql } from 'apollo-server-core';
import { AllowNull, BelongsToMany, Column, ForeignKey, Index, Model, PrimaryKey, Table, Unique } from 'sequelize-typescript';
import { Resolvers } from '../generated/graphql-types';
import { File } from './file';
import { Problem } from './problem';
import { User } from './user';

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

    @AllowNull
    @Column
    extraTime: Date;
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
}

/** Contest to File N-N relation */
@Table({ timestamps: false })
export class ContestFile extends Model<ContestFile> {
    @ForeignKey(() => Contest)
    @PrimaryKey
    @Column
    contestId!: number;

    @ForeignKey(() => File)
    @PrimaryKey
    @Column
    fileId!: number;
}

/** A contest in TuringArena */
@Table
export class Contest extends Model<Contest> {
    /** Name of the contest, must be a valid identifier, e.g. ioi */
    @Unique
    @Index
    @Column
    name!: string;

    /** Title of the contest, as a string, e.g. 'International Olimpics in Informatics' */
    @Column
    title!: string;

    /** When the contest will start */
    @Column
    start!: Date;

    /** When the contest will end */
    @Column
    end!: Date;

    /** The list of problems in this contest */
    @BelongsToMany(() => Problem, () => ContestProblem)
    problems!: Problem[];

    /** The list of users in this contest */
    @BelongsToMany(() => User, () => Participation)
    users!: User[];

    /** The list of files in this contest */
    @BelongsToMany(() => File, () => ContestFile)
    files!: File[];
}
