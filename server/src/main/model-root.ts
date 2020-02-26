import { Model, Sequelize } from 'sequelize-typescript';
import { AuthService } from '../core/auth';
import { modelConstructors } from '../core/index';
import { Submission } from '../core/submission';
import { Config, defaultConfig } from './config';

export interface ModelRootSequelize extends Sequelize {
    root: ModelRoot;
}

/**
 * Entry point of the model layer.
 */
export class ModelRoot {
    constructor(
        /** Current server configuration */
        readonly config: Config = defaultConfig,
    ) {
        this.table(Submission).afterSync('create foreign key', () => {
            this.sequelize.query(
                'ALTER TABLE submissions ADD CONSTRAINTS participation_fk FOREIGN KEY (user_id, contest_id) REFERENCES participations(user_id, contest_id)',
            );
        });

        this.sequelize.root = this;
    }

    // TODO: load secret from environment
    readonly authService = new AuthService(this);

    /** Instance of Sequelize to use in this API operation. */
    readonly sequelize = new Sequelize({
        ...this.config.db,
        models: Object.values(modelConstructors),
        benchmark: true,
        repositoryMode: true,
        define: {
            underscored: true,
        },
    }) as ModelRootSequelize;

    /** Shortcut for `this.sequelize.getRepository(modelClass)`. */
    table<M extends Model>(modelClass: new () => M) {
        return this.sequelize.getRepository(modelClass);
    }

    /** Convenience method to fail a request. */
    fail(message?: string): never {
        throw new Error(message);
    }
}
