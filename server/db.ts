import { Sequelize } from 'sequelize-typescript';
import { User } from './api/user';

export const sequelize = new Sequelize({
    dialect: 'sqlite',
    storage: ':memory:',
    models: [User],
    benchmark: true,
    logQueryParameters: true,
});
