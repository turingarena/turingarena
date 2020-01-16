import { gql } from 'apollo-server-core';
import { createHash } from 'crypto';
import { Column, Index, Model, Table, Unique } from 'sequelize-typescript';

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

    static create(file) {
        const hash = createHash('sha1').update(file.content).digest('hex');

        // https://github.com/RobinBuschmann/sequelize-typescript/issues/291
        return super.create.call(File, {
            content: file.content,
            fileName: file.fileName,
            type: file.type,
            hash,
        });
    }
}

// TODO: resolvers to add and retrieve files
