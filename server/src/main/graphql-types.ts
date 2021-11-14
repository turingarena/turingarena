import { graphqlIntrospection } from '../generated/graphql.schema';
import { GraphQLInputValue, GraphQLOutputValue } from '../util/graphql-introspection-types';
import { ApiContext } from './api-context';

type AllTypes = typeof graphqlIntrospection['__schema']['types'][number];

export type ApiOutputValue<T extends AllTypes['name']> = GraphQLOutputValue<
    { allTypes: AllTypes; context: ApiContext },
    T
>;

export type ApiInputValue<T extends AllTypes['name']> = GraphQLInputValue<
    { allTypes: AllTypes; context: ApiContext },
    T
>;
