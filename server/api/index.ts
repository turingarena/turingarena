import { gql } from 'apollo-server-core';
import { DocumentNode, execute } from 'graphql';
import { IResolvers, makeExecutableSchema } from 'graphql-tools';
import { Model, Repository, Sequelize } from 'sequelize-typescript';
import { Resolvers } from '../generated/graphql-types';
import { Contest, ContestFile, ContestProblem, contestResolvers, contestSchema, Participation } from './contest';
import { File, fileSchema } from './file';
import { mutationResolvers, mutationSchema } from './mutation';
import { Problem, ProblemFile, problemSchema } from './problem';
import { queryResolvers, querySchema } from './query';
import { Evaluation, EvaluationEvent, Submission, SubmissionFile } from './submission';
import { User, userResolvers, userSchema } from './user';

/** Full GraphQL schema document. Obtained combining schema parts from each components. */
export const schema = gql`
    ${querySchema}
    ${mutationSchema}
    ${userSchema}
    ${contestSchema}
    ${problemSchema}
    ${fileSchema}
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
    /** Executable schema, obtained combining full GraphQL schema and resolvers. */
    readonly executableSchema = makeExecutableSchema({
        typeDefs: schema,
        resolvers: resolvers as IResolvers,
    });

    /** Instance of Sequelize to use in this API operation. */
    readonly sequelize = new Sequelize({
        dialect: 'sqlite',
        storage: ':memory:',
        models: Object.values(modelConstructors),
        benchmark: true,
        logQueryParameters: true,
        repositoryMode: true,
    });

    /** Contains an entry for each available repository of models. */
    readonly db = Object.fromEntries(
        Object.entries(modelConstructors).map(([key, modelConstructor]) =>
            [key, this.sequelize.getRepository<Model>(modelConstructor)],
        ),
    ) as ModelRepositoryRecord;

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
