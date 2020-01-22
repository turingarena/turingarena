import { DocumentNode, execute } from 'graphql';
import { IResolvers, makeExecutableSchema } from 'graphql-tools';
import { Model, Sequelize } from 'sequelize-typescript';
import { modelConstructors, resolvers, schema } from '../core/index';
import { Submission } from '../core/submission';
import { Config, defaultConfig } from './config';

// Definitions related to models, their classes, and their repositories.

export interface OperationRequest<V> {
    document: DocumentNode;
    operationName?: string | null;
    variableValues?: V;
}

export interface SequelizeWithContext extends Sequelize {
    context: ApiContext;
}

/**
 * Context for the execution of an API operation.
 * Allows for accessing configuration and database, check authentication, and more.
 */
export class ApiContext {
    constructor(
        /** Current server configuration */
        readonly config: Config = defaultConfig,
    ) {
        this.table(Submission).afterSync('create foreign key', () => {
            this.sequelize.query(
                'ALTER TABLE Submissions ADD CONSTRAINTS participation_fk FOREIGN KEY (userId, contestId) REFERENCES Participations(userId, contestId)',
            );
        });

        this.sequelize.context = this;
    }

    /** Instance of Sequelize to use in this API operation. */
    readonly sequelize = new Sequelize({
        ...this.config.db,
        models: Object.values(modelConstructors),
        benchmark: true,
        repositoryMode: true,
    }) as SequelizeWithContext;

    /** Executable schema, obtained combining full GraphQL schema and resolvers. */
    readonly executableSchema = makeExecutableSchema({
        typeDefs: schema,
        resolvers: resolvers as IResolvers,
    });

    /** Shortcut for `this.sequelize.getRepository(modelClass)`. */
    table<M extends Model>(modelClass: new () => M) {
        return this.sequelize.getRepository(modelClass);
    }

    /** Run a GraphQL operation in this context. */
    async execute<T = unknown, V = {}>({ document, operationName, variableValues }: OperationRequest<V>) {
        return execute<T>({
            document,
            operationName,
            variableValues,
            schema: this.executableSchema,
            contextValue: this,
            rootValue: {},
        });
    }

    /** Convenience method to fail a request. */
    fail(message?: string): never {
        throw new Error(message);
    }
}
