import { DocumentNode, execute } from 'graphql';
import { User } from '../core/user';
import { ApiCache } from './api-cache';
import { executableSchema } from './executable-schema';
import { ServiceContext } from './service-context';

export interface OperationRequest<V> {
    document: DocumentNode;
    operationName?: string | null;
    variableValues?: V;
}

/**
 * Entry point for the execution of an API operation.
 * Also, contains extra information associated with an API request (e.g., authentication data).
 */
export abstract class ApiContext {
    constructor(readonly serviceContext: ServiceContext) {}

    abstract authorizeUser(username: string): Promise<void>;
    abstract authorizeAdmin(): Promise<void>;

    readonly caches = new Map<unknown, unknown>();

    config = this.serviceContext.config;
    service = this.serviceContext.service;
    db = this.serviceContext.db;
    table = this.serviceContext.table;

    auth = this.serviceContext.auth;

    cache<T extends ApiCache>(cacheClass: new (ctx: ApiContext) => T): T {
        if (!this.caches.has(cacheClass)) {
            this.caches.set(cacheClass, new cacheClass(this));
        }

        return this.caches.get(cacheClass) as T;
    }
}

/**
 * Context for API requests made programmatically. Authentication is skipped.
 */
export class LocalApiContext extends ApiContext {
    async authorizeUser(username: string) {
        return;
    }
    async authorizeAdmin() {
        return;
    }
}

/**
 * Context for API requests made via network.
 */
export class RemoteApiContext extends ApiContext {
    constructor(serviceContext: ServiceContext, readonly admin: boolean, readonly user?: User) {
        super(serviceContext);
    }

    async authorizeUser(username: string) {
        if (this.user?.username === username) return;
        if (this.admin) return;

        throw new Error(`Not logged in as '${username}', nor admin`);
    }

    async authorizeAdmin() {
        if (this.admin) return;

        throw new Error(`Not authorized`);
    }

    schema = executableSchema();

    /** Run a GraphQL operation in this context. */
    async execute<T = unknown, V = {}>({ document, operationName, variableValues }: OperationRequest<V>) {
        return execute<T>({
            document,
            operationName,
            variableValues,
            schema: this.schema,
            contextValue: this,
            rootValue: {},
        });
    }
}
