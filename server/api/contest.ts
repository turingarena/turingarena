import { gql } from 'apollo-server-core';
import { Column, IsUUID, Model, PrimaryKey, Table } from 'sequelize-typescript';
import { Resolvers } from '../generated/graphql-types';

export const contestSchema = gql`
    type Contest {
        id: ID!
        name: String!
    }
`;

@Table
export class Contest extends Model<Contest> {
    @IsUUID('4')
    @PrimaryKey
    @Column
    id!: string;

    @Column
    title!: string;
}

export const contestResolvers: Resolvers = {
    Contest: {
        id: (contest) => contest.id,
    },
};
