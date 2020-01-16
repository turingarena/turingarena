import { gql } from 'apollo-server-core';
import {
    BelongsToMany,
    Column,
    ForeignKey,
    Index,
    Model,
    PrimaryKey,
    Table,
    Unique
} from 'sequelize-typescript';
import { Contest, ContestProblem } from './contest';
import { File } from './file';

export const problemSchema = gql`
    type Problem {
        name: ID!
        files: [File!]!
    }

    input ProblemInput {
        name: ID!
        files: [ID!]!
    }
`;

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

    @Column
    path!: string;
}

@Table
@BelongsToMany(() => Contest, () => ContestProblem)
export class Problem extends Model<Problem> {
    @Unique
    @Column
    @Index
    name!: string;

    @BelongsToMany(() => File, () => ProblemFile)
    files: ProblemFile;
}
