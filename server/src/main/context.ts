import { DocumentNode, execute } from 'graphql';
import { IResolvers, makeExecutableSchema } from 'graphql-tools';
import { Model, Repository, Sequelize } from 'sequelize-typescript';
import { modelConstructors, resolvers, schema } from '../core/index';
import { Config, defaultConfig } from './config';

// Definitions related to models, their classes, and their repositories.

export type ModelConstructorRecord = typeof modelConstructors;
export type ModelName = keyof ModelConstructorRecord;
export type ModelRecord = {
    [K in ModelName]: InstanceType<ModelConstructorRecord[K]>;
};
export type ModelRepositoryRecord = {
    [K in ModelName]: Repository<ModelRecord[K]>;
};

export interface OperationRequest<V> {
    document: DocumentNode;
    operationName?: string | null;
    variableValues?: V;
}

/**
 * Context for the execution of an API operation.
 * Allows for accessing configuration and database, check authentication, and more.
 */
export class ApiContext {
    /** Instance of Sequelize to use in this API operation. */
    readonly sequelize: Sequelize;

    /** Contains an entry for each available repository of models. */
    readonly db: ModelRepositoryRecord;

    /** Current server configuration */
    readonly config: Config;

    constructor(config: Config = defaultConfig) {
        this.config = config;

        const models = Object.values(modelConstructors);

        this.sequelize = new Sequelize({
            ...config.db,
            models,
            benchmark: true,
            repositoryMode: true,
        });

        this.db = Object.fromEntries(
            Object.entries(modelConstructors).map(([key, modelConstructor]) => [
                key,
                this.sequelize.getRepository<Model>(modelConstructor),
            ]),
        ) as ModelRepositoryRecord;
    }

    /** Executable schema, obtained combining full GraphQL schema and resolvers. */
    readonly executableSchema = makeExecutableSchema({
        typeDefs: schema,
        resolvers: resolvers as IResolvers,
    });

    /** Run a GraphQL operation in this context. */
    async execute<T = unknown, V = {}>({
        document,
        operationName,
        variableValues,
    }: OperationRequest<V>) {
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
