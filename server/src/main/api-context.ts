import { DocumentNode, execute } from 'graphql';
import { IResolvers, makeExecutableSchema } from 'graphql-tools';
import { resolvers, schema } from '../core';
import { ModelRoot } from './model-root';

export interface OperationRequest<V> {
    document: DocumentNode;
    operationName?: string | null;
    variableValues?: V;
}

/**
 * Entry point for the execution of an API operation.
 * Also, contains extra information associated with an API request (e.g., authentication data).
 */
export class ApiContext {
    constructor(readonly root: ModelRoot) {}

    /** Executable schema, obtained combining full GraphQL schema and resolvers. */
    readonly executableSchema = makeExecutableSchema({
        typeDefs: schema,
        resolvers: resolvers as IResolvers,
    });

    /** Run a GraphQL operation in this context. */
    async execute<T = unknown, V = {}>({ document, operationName, variableValues }: OperationRequest<V>) {
        return execute<T>({
            document,
            operationName,
            variableValues,
            schema: this.executableSchema,
            contextValue: this,
            rootValue: this.root,
        });
    }
}
