import { ResolverFn, Resolvers, TypeResolveFn } from '../generated/graphql-types';

export type ResolversWithModels<
    T extends {
        [K in keyof Resolvers]: unknown;
    }
> = {
    [KType in keyof T & keyof Resolvers]: {
        [KField in keyof Required<Resolvers>[KType]]: Required<
            Required<Resolvers>[KType]
        >[KField] extends TypeResolveFn<infer TTypeResult, infer TTypeParent, infer TTypeContext>
            ? TypeResolveFn<TTypeResult, T[KType], TTypeContext>
            : Required<Required<Resolvers>[KType]>[KField] extends ResolverFn<
                  infer TResult,
                  infer TParent,
                  infer TContext,
                  infer TArgs
              >
            ? ResolverFn<TResult, T[KType], TContext, TArgs>
            : never;
    };
};
