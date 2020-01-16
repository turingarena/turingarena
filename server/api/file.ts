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

    static async create(content: Buffer, fileName: string, type: string): Promise<string> {
        const hash = createHash('sha1').update(content).digest('hex');

        await super.create({
            content,
            fileName,
            type,
            hash,
        });

        return hash;
    }
}

// TODO: resolvers to add and retrieve files
