import { gql } from 'apollo-server-core';
import { Column, IsUUID, Model, PrimaryKey, Table } from 'sequelize-typescript';
import { UserResolvers, UserUpdate } from '../generated/graphql-types';

export const userSchema = gql`
  type User {
    id: ID!
    name: String!
  }
`;

@Table
export class User extends Model<User> {
  @IsUUID('4')
  @PrimaryKey
  @Column
  id!: string;

  @Column
  name!: string;
}

export const userResolvers: UserResolvers<undefined, User> = {
  id: (user) => user.id,
};
