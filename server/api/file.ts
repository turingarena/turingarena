import { gql } from 'apollo-server-core';
import { createHash } from 'crypto';
import { AutoIncrement, Column, Index, Model, NotNull, PrimaryKey, Table, Unique } from 'sequelize-typescript';

export const fileSchema = gql`
    type File {
        hash: ID!
        fileName: String!
        type: String!
        contentBase64: String!
    }

    input FileInput {
        fileName: String!
        type: String!
        contentBase64: String!
    }
`;

@Table({ updatedAt: false })
export class File extends Model<File> {
    @Unique
    @Index
    @Column
    hash!: string;

    @Column
    type!: string;

    @Column
    fileName!: string;

    @Column
    content!: Buffer;

    static create(file): Promise<File> {
        const hash = createHash('sha1').update(file.content).digest('hex');

        // https://github.com/RobinBuschmann/sequelize-typescript/issues/291
        return super.create.call(this, {
            content: file.content,
            filename: file.fileName,
            type: file.type,
            hash,
        });
    }
}

// TODO: resolvers to add and retrieve files
