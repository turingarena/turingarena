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
}

export type GraphQLOutputValueWrapper<T> = T | Promise<T>;
export type GraphQLInputValueWrapper<T> = T;

export interface GraphQLArrayOutputValue<T>
    extends Array<GraphQLOutputValueWrapper<T> | Promise<GraphQLOutputValueWrapper<T>>> {}
export interface GraphQLArrayInputValue<T> extends Array<GraphQLInputValueWrapper<T>> {}

export type GraphQLOutputValueOfType<
    TConfig extends GraphQLConfigMap,
    T extends IntrospectionType
> = T extends IntrospectionObjectType
    ? GraphQLValueOfObjectTypeOmitTypename<TConfig, T> & { __typename?: T['name'] }
    : T extends IntrospectionUnionType | IntrospectionInterfaceType
    ? NonNull<GraphQLOutputValueOfTypeRefUnspecifiedNullability<TConfig, T['possibleTypes'][number]>>
    : T extends IntrospectionEnumType
    ? T['enumValues'][number]['name']
    : T extends IntrospectionScalarType
    ? ScalarMap extends { [K in T['name']]: infer V }
        ? V
        : never
    : never;

export type GraphQLInputValueOfType<
    TConfig extends GraphQLConfigMap,
    T extends IntrospectionType
> = T extends IntrospectionInputObjectType
    ? {
          [K in T['inputFields'][number]['name']]: GraphQLInputValueOfTypeRef<
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

export type GraphQLOutputValueOfTypeRefUnspecifiedNullability<
    TConfig extends GraphQLConfigMap,
    T extends IntrospectionTypeRef
> = T extends IntrospectionNamedTypeRef
    ? UnspecifiedNullability<GraphQLOutputValueOfType<TConfig, ExtractNamed<TConfig['allTypes'], T['name']>>>
    : T extends IntrospectionListTypeRef
    ? UnspecifiedNullability<GraphQLArrayOutputValue<GraphQLOutputValueOfTypeRef<TConfig, T['ofType']>>>
    : never;

export type GraphQLInputValueOfTypeRefUnspecifiedNullability<
    TConfig extends GraphQLConfigMap,
    T extends IntrospectionTypeRef
> = T extends IntrospectionNamedTypeRef
    ? UnspecifiedNullability<GraphQLInputValueOfType<TConfig, ExtractNamed<TConfig['allTypes'], T['name']>>>
    : T extends IntrospectionListTypeRef
    ? UnspecifiedNullability<GraphQLArrayInputValue<GraphQLInputValueOfTypeRef<TConfig, T['ofType']>>>
    : never;

export type GraphQLOutputValueOfTypeRef<
    TConfig extends GraphQLConfigMap,
    T extends IntrospectionTypeRef
> = T extends IntrospectionNonNullTypeRef
    ? NonNull<GraphQLOutputValueOfTypeRefUnspecifiedNullability<TConfig, T['ofType']>>
    : Nullable<GraphQLOutputValueOfTypeRefUnspecifiedNullability<TConfig, T>>;

export type GraphQLInputValueOfTypeRef<
    TConfig extends GraphQLConfigMap,
    T extends IntrospectionTypeRef
> = T extends IntrospectionNonNullTypeRef
    ? NonNull<GraphQLInputValueOfTypeRefUnspecifiedNullability<TConfig, T['ofType']>>
    : Nullable<GraphQLInputValueOfTypeRefUnspecifiedNullability<TConfig, T>>;

export type GraphQLFieldResolver<TValue, TArgs, TContext> = TValue | ((args: TArgs, ctx: TContext) => TValue);

export type GraphQLResolverOfField<
    TConfig extends GraphQLConfigMap,
    T extends IntrospectionField
> = GraphQLFieldResolver<
    GraphQLOutputValueWrapper<GraphQLOutputValueOfTypeRef<TConfig, T['type']>>,
    {
        [K in T['args'][number]['name']]: GraphQLInputValueOfTypeRef<
            TConfig,
            ExtractNamed<T['args'][number], K>['type']
        >;
    },
    TConfig['context']
>;

export type GraphQLOutputValue<
    TConfig extends GraphQLConfigMap,
    TName extends TConfig['allTypes']['name']
> = GraphQLOutputValueOfType<TConfig, ExtractNamed<TConfig['allTypes'], TName>>;

export type GraphQLInputValue<
    TConfig extends GraphQLConfigMap,
    TName extends TConfig['allTypes']['name']
> = GraphQLInputValueOfType<TConfig, ExtractNamed<TConfig['allTypes'], TName>>;
