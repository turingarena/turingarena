import { Resolver, Resolvers } from '../generated/graphql-types';

export type ResolversWithModels<
    T extends {
        [K in keyof Resolvers]: unknown;
    }
> = {
    [KType in keyof T & keyof Resolvers]: {
        [KField in keyof Resolvers[KType]]: Resolvers[KType][KField] extends Resolver<
            infer TResult,
            infer TParent,
            infer TContext,
            infer TArgs
        >
            ? Resolver<TResult, T[KType], TContext, TArgs>
            : never;
    };
};
