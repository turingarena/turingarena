import { DocumentNode, execute } from 'graphql';
import { Model, Sequelize } from 'sequelize-typescript';
import { AuthService } from '../core/auth';
import { modelConstructors } from '../core/model';
import { User, UserCache } from '../core/user';
import { ApiCache } from './api-cache';
import { Config, defaultConfig } from './config';
import { executableSchema } from './executable-schema';

export interface OperationRequest<V> {
    document: DocumentNode;
    operationName?: string | null;
    variableValues?: V;
}

/** Contains the configuration of the server, but does not hold any resources */
export class ApiEnvironment {
    constructor(readonly config: Config = defaultConfig) {}

    /** Instance of Sequelize to use in this API operation. */
    readonly sequelize = new Sequelize({
        ...this.config.db,
        models: Object.values(modelConstructors),
        benchmark: true,
        repositoryMode: true,
        define: {
            underscored: true,
        },
    });

    // TODO: load secret from environment
    readonly authService = new AuthService(this);
}

/**
 * Entry point for the execution of an API operation.
 * Also, contains extra information associated with an API request (e.g., authentication data).
 */
export abstract class ApiContext {
    constructor(readonly environment: ApiEnvironment) {}

    abstract authorizeUser(username: string): Promise<void>;
    abstract authorizeAdmin(): Promise<void>;

    readonly caches = new Map<unknown, unknown>();

    cache<T extends ApiCache>(cacheClass: new (ctx: ApiContext) => T): T {
        if (!this.caches.has(cacheClass)) {
            this.caches.set(cacheClass, new cacheClass(this));
        }

        return this.caches.get(cacheClass) as T;
    }

    /** Shortcut for `this.sequelize.getRepository(modelClass)`. */
    table<M extends Model>(modelClass: new () => M) {
        return this.environment.sequelize.getRepository(modelClass);
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

export class RemoteApiContext extends ApiContext {
    constructor(readonly environment: ApiEnvironment, readonly user?: User) {
        super(environment);
    }

    private async isAdmin() {
        if (this.environment.config.skipAuth) return true;

        if (this.user === undefined) return false;
        const { role } = await this.cache(UserCache).byId.load(this.user.id);

        return role === 'admin';
    }

    async authorizeUser(username: string) {
        if (this.environment.config.skipAuth) return;

        if (this.user?.username === username) return;
        if (await this.isAdmin()) return;

        throw new Error(`Not logged in as '${username}', nor admin`);
    }

    async authorizeAdmin() {
        if (this.environment.config.skipAuth) return;
        if (await this.isAdmin()) return;

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
