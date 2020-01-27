import { gql } from 'apollo-server-core';
import { AllowNull, BelongsTo, Column, ForeignKey, PrimaryKey, Table } from 'sequelize-typescript';
import { FindOptions } from 'sequelize/types';
import { BaseModel } from '../main/base-model';
import { Resolvers } from '../main/resolver-types';
import { FileContent } from './file-content';
import { Problem } from './problem';

export const problemFileSchema = gql`
    type ProblemFile {
        problem: Problem!
        path: String!
        content: FileContent!
    }
`;

/** Problem to File N-N relation. */
@Table({ timestamps: false })
export class ProblemFile extends BaseModel<ProblemFile> {
    @ForeignKey(() => Problem)
    @PrimaryKey
    @Column
    problemId!: number;

    @ForeignKey(() => FileContent)
    @AllowNull(false)
    @Column
    contentId!: number;

    @PrimaryKey
    @Column
    path!: string;

    @BelongsTo(() => Problem)
    problem!: Problem;
    getProblem!: (options?: object) => Promise<Problem>;

    @BelongsTo(() => FileContent)
    content!: FileContent;
    getContent!: (options?: FindOptions) => Promise<FileContent>;
}

export interface ProblemFileModelRecord {
    ProblemFile: ProblemFile;
}

export const problemFileResolvers: Resolvers = {
    ProblemFile: {
        content: file => file.getContent(),
        problem: file => file.getProblem(),
    },
};
