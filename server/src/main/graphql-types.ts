import { graphqlIntrospection } from '../generated/graphql.schema';
import { GraphQLValue } from '../util/graphql-introspection-types';

type AllTypes = typeof graphqlIntrospection['__schema']['types'][number];

export type ApiGraphQLValue<T extends AllTypes['name']> = GraphQLValue<{ allTypes: AllTypes; context: unknown }, T>;
