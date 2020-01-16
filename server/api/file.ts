import { gql } from 'apollo-server-core';
import { AutoIncrement, Column, Index, Model, NotNull, PrimaryKey, Table, Unique } from 'sequelize-typescript';

export const fileSchema = gql`
    type File {
        hash: ID!
        contentBase64: String!
    }

    input FileInput {
        hash: ID!
        contentBase64: String!
    }
`;

@Table
export class File extends Model<File> {
    @PrimaryKey
    @AutoIncrement
    @Column
    fileId!: number;

    @Unique
    @Index
    @Column
    hash!: string;

    @Column
    fileName!: string;

    @Column
    content!: Buffer;
}
