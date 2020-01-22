import { Model, Sequelize } from 'sequelize-typescript';
import { modelConstructors } from '../core/index';
import { Submission } from '../core/submission';
import { Config, defaultConfig } from './config';

export interface ModelRootSequelize extends Sequelize {
    modelRoot: ModelRoot;
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
                'ALTER TABLE Submissions ADD CONSTRAINTS participation_fk FOREIGN KEY (userId, contestId) REFERENCES Participations(userId, contestId)',
            );
        });

        this.sequelize.modelRoot = this;
    }

    /** Instance of Sequelize to use in this API operation. */
    readonly sequelize = new Sequelize({
        ...this.config.db,
        models: Object.values(modelConstructors),
        benchmark: true,
        repositoryMode: true,
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
