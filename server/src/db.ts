import { Column, Model, Sequelize, Table } from 'sequelize-typescript';

@Table
export class User extends Model<User> {
  @Column
  nickname!: string;
}

const models = [User];

export const sequelize = new Sequelize({
  // database: 'some_db',
  dialect: 'sqlite',
  // username: 'root',
  // password: '',
  storage: ':memory:',
  models,
});
