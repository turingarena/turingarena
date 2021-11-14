import {
    IntrospectionEnumType,
    IntrospectionField,
    IntrospectionInputObjectType,
    IntrospectionInterfaceType,
    IntrospectionListTypeRef,
    IntrospectionNamedTypeRef,
    IntrospectionNonNullTypeRef,
    IntrospectionObjectType,
    IntrospectionScalarType,
    IntrospectionType,
    IntrospectionTypeRef,
    IntrospectionUnionType,
} from 'graphql';

export interface GraphQLConfigMap {
    allTypes: IntrospectionType;
    context: any;
}

export type ExtractNamed<TConfig extends { name: string }, TName extends string> = TConfig extends { name: TName }
    ? TConfig
    : never;

export interface ScalarMap {
    String: string;
    ID: string;
    Int: number;
    Float: number;
    Boolean: boolean;
    File: File;
}

export type GraphQLOutputValue<T> = { graphql: T } | T;

export interface GraphQLArrayOutputValue<T> extends Array<GraphQLOutputValue<T> | Promise<GraphQLOutputValue<T>>> {}

export type GraphQLValueOfType<
    TConfig extends GraphQLConfigMap,
    T extends IntrospectionType
> = T extends IntrospectionObjectType
    ? GraphQLValueOfObjectTypeOmitTypename<TConfig, T> & { __typename?: T['name'] }
    : T extends IntrospectionUnionType | IntrospectionInterfaceType
    ? NonNull<GraphQLValueOfTypeRefUnspecifiedNullability<TConfig, T['possibleTypes'][number]>>
    : T extends IntrospectionInputObjectType
    ? {
          [K in T['inputFields'][number]['name']]: GraphQLValueOfTypeRef<
              TConfig,
              ExtractNamed<T['inputFields'][number], K>['type']
          >;
      }
    : T extends IntrospectionEnumType
    ? T['enumValues'][number]['name']
    : T extends IntrospectionScalarType
    ? ScalarMap extends { [K in T['name']]: infer V }
        ? V
        : never
    : never;

export type GraphQLValueOfObjectTypeOmitTypename<
    TConfig extends GraphQLConfigMap,
    T extends IntrospectionObjectType
> = {
    [K in T['fields'][number]['name']]: GraphQLResolverOfField<TConfig, ExtractNamed<T['fields'][number], K>>;
};

export interface UnspecifiedNullability<T> {
    __unspecifiedNullability: T;
}

export type NonNull<T> = T extends UnspecifiedNullability<infer U> ? U : never;
export type Nullable<T> = T extends UnspecifiedNullability<infer U> ? U | null : never;

export type GraphQLValueOfTypeRefUnspecifiedNullability<
    TConfig extends GraphQLConfigMap,
    T extends IntrospectionTypeRef
> = T extends IntrospectionNamedTypeRef
    ? UnspecifiedNullability<GraphQLValueOfType<TConfig, ExtractNamed<TConfig['allTypes'], T['name']>>>
    : T extends IntrospectionListTypeRef
    ? UnspecifiedNullability<GraphQLArrayOutputValue<GraphQLValueOfTypeRef<TConfig, T['ofType']>>>
    : never;

export type GraphQLValueOfTypeRef<
    TConfig extends GraphQLConfigMap,
    T extends IntrospectionTypeRef
> = T extends IntrospectionNonNullTypeRef
    ? NonNull<GraphQLValueOfTypeRefUnspecifiedNullability<TConfig, T['ofType']>>
    : Nullable<GraphQLValueOfTypeRefUnspecifiedNullability<TConfig, T>>;

export type GraphQLFieldResolver<TValue, TArgs, TContext> =
    | TValue
    | Promise<TValue>
    | ((args: TArgs, ctx: TContext) => TValue)
    | ((args: TArgs, ctx: TContext) => Promise<TValue>);

export type GraphQLResolverOfField<
    TConfig extends GraphQLConfigMap,
    T extends IntrospectionField
> = GraphQLFieldResolver<
    GraphQLOutputValue<GraphQLValueOfTypeRef<TConfig, T['type']>>,
    {
        [K in T['args'][number]['name']]: GraphQLValueOfTypeRef<TConfig, ExtractNamed<T['args'][number], K>['type']>;
    },
    TConfig['context']
>;

export type IntrospectionTypeMap<TConfig extends GraphQLConfigMap> = {
    [K in TConfig['allTypes']['name']]: GraphQLValueOfType<TConfig, ExtractNamed<TConfig['allTypes'], K>>;
};

export type GraphQLValue<
    TConfig extends GraphQLConfigMap,
    TName extends TConfig['allTypes']['name']
> = GraphQLValueOfType<TConfig, ExtractNamed<TConfig['allTypes'], TName>>;
