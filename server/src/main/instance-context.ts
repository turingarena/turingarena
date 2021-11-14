import { Model, Sequelize } from 'sequelize-typescript';
import { modelConstructors } from '../core/model';
import { Config, defaultConfig } from './config';

/** Allows access to server config and data, but does not hold any resources. */
export class InstanceContext {
    constructor(readonly config: Config = defaultConfig) {}

    readonly db = new Sequelize({
        ...this.config.db,
        models: Object.values(modelConstructors),
        benchmark: true,
        repositoryMode: true,
        define: {
            underscored: true,
        },
    });

    table = <M extends Model>(modelClass: new () => M) => this.db.getRepository(modelClass);
}
