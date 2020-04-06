import { NgModule } from '@angular/core';
import { ApolloModule, APOLLO_OPTIONS } from 'apollo-angular';
import { HttpLink, HttpLinkModule } from 'apollo-angular-link-http';
import { InMemoryCache, IntrospectionFragmentMatcher } from 'apollo-cache-inmemory';
import { persistCache } from 'apollo-cache-persist';
import { ApolloClientOptions } from 'apollo-client';
import { ApolloLink } from 'apollo-link';
import { setContext } from 'apollo-link-context';
import gql from 'graphql-tag';
import schema from '../../../server/src/generated/graphql.schema.json'; // tslint:disable-line: no-default-import
import { CurrentAuthQuery } from '../generated/graphql-types.js';

export const currentAuthQuery = gql`
  query CurrentAuth {
    currentAuth {
      token
      user {
        name
        username
      }
    }
  }
`;

const createApollo = (httpLink: HttpLink): ApolloClientOptions<unknown> => {
  const cache = new InMemoryCache({
    fragmentMatcher: new IntrospectionFragmentMatcher({
      introspectionQueryResultData: schema,
    }),
    freezeResults: true,
    // dataIdFromObject: () => undefined,
  });

  persistCache({
    cache,
    storage: window.sessionStorage as any,
    debug: true,
    key: 'cache',
  }).catch(e => {
    console.error(e);
  });

  const link = ApolloLink.from([
    setContext((operation, context) => {
      const token =
        cache.readQuery<CurrentAuthQuery>({
          query: currentAuthQuery,
        })?.currentAuth?.token ?? null;

      return {
        headers: token !== null ? { Authorization: `Bearer ${token}` } : {},
      };
    }),
    httpLink.create({ uri: '/graphql' }),
  ]);

  return {
    link,
    cache,
    resolvers: {
      Query: {
        currentAuth: () =>
          cache.readQuery<CurrentAuthQuery>({
            query: currentAuthQuery,
          })?.currentAuth ?? null,
      },
    },
  };
};

@NgModule({
  exports: [ApolloModule, HttpLinkModule],
  providers: [
    {
      provide: APOLLO_OPTIONS,
      useFactory: createApollo,
      deps: [HttpLink],
    },
  ],
})
export class GraphQLModule {}
