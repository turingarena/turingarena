import { gql } from 'apollo-server-core';
import { DocumentNode, execute } from 'graphql';
import { IResolvers, makeExecutableSchema } from 'graphql-tools';
import { Model, Repository, Sequelize } from 'sequelize-typescript';
import { Config } from '../config';
import { Resolvers } from '../generated/graphql-types';
import { Contest, ContestFile, ContestProblem, Participation } from '../model/contest';
import { Evaluation, EvaluationEvent } from '../model/evaluation';
import { File } from '../model/file';
import { Problem, ProblemFile } from '../model/problem';
import { Submission, SubmissionFile } from '../model/submission';
import { User } from '../model/user';
import { contestResolvers, contestSchema } from './contest';
import { fileSchema } from './file';
import { mutationResolvers, mutationSchema } from './mutation';
import { problemSchema } from './problem';
import { queryResolvers, querySchema } from './query';
import { submissionSchema } from './submission';
import { userResolvers, userSchema } from './user';

/** Full GraphQL schema document. Obtained combining schema parts from each components. */
export const schema = gql`
    ${querySchema}
    ${mutationSchema}
    ${userSchema}
    ${contestSchema}
    ${problemSchema}
    ${fileSchema}
    ${submissionSchema}
`;

/** All GraphQL resolvers. Obtained combining resolvers from each components. */
export const resolvers: Resolvers = {
    ...queryResolvers,
    ...mutationResolvers,
    ...userResolvers,
    ...contestResolvers,
};

// Definitions related to models, their classes, and their repositories.

export const modelConstructors = {
    User,
    Contest,
    Problem,
    ContestProblem,
    Participation,
    File,
    ProblemFile,
    ContestFile,
    Submission,
    SubmissionFile,
    Evaluation,
    EvaluationEvent,
} as const;

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

    constructor(config?: Config) {
        this.sequelize = new Sequelize({
            dialect: config?.dbDialect || 'sqlite',
            storage: config?.dbPath || ':memory:',
            models: Object.values(modelConstructors),
            benchmark: true,
            logQueryParameters: true,
            repositoryMode: true,
        });

        this.db = Object.fromEntries(
            Object.entries(modelConstructors).map(([key, modelConstructor]) =>
                [key, this.sequelize.getRepository<Model>(modelConstructor)],
            ),
        ) as ModelRepositoryRecord;
    }

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
            rootValue: {},
        });
    }
}

// tslint:disable-next-line: no-default-export
export default schema; // For graphql-codegen
