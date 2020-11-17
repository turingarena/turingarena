import { DocumentNode, execute } from 'graphql';
import { Model, Sequelize } from 'sequelize-typescript';
import { modelConstructors } from '../core';
import { AuthService } from '../core/auth';
import { User, UserCache } from '../core/user';
import { ApiObject } from './api';
import { Config, defaultConfig } from './config';
import { createSchema } from './executable-schema';

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
    constructor(readonly environment: ApiEnvironment) {
        // this.table(Submission).afterSync('create foreign key', () => {
        //     this.sequelize.query(
        //         'ALTER TABLE submissions ADD CONSTRAINTS participation_fk FOREIGN KEY (user_id, contest_id) REFERENCES participations(user_id, contest_id)',
        //     );
        // });
    }

    abstract authorizeUser(username: string): Promise<void>;
    abstract authorizeAdmin(): Promise<void>;

    readonly apiObjectCache = new Map<unknown, unknown>();

    api<T extends ApiObject>(apiClass: new (ctx: ApiContext) => T): T {
        if (!this.apiObjectCache.has(apiClass)) {
            this.apiObjectCache.set(apiClass, new apiClass(this));
        }

        return this.apiObjectCache.get(apiClass) as T;
    }

    /** Shortcut for `this.sequelize.getRepository(modelClass)`. */
    table<M extends Model>(modelClass: new () => M) {
        return this.environment.sequelize.getRepository(modelClass);
    }

    /** Convenience method to fail a request. */
    fail(message?: string): never {
        throw new Error(message);
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
        const { role } = await this.api(UserCache).metadataLoader.load(this.user);

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

    schema = createSchema();

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
