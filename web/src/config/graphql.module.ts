import { NgModule } from '@angular/core';
import { APOLLO_OPTIONS, ApolloModule } from 'apollo-angular';
import { HttpLink, HttpLinkModule } from 'apollo-angular-link-http';
import { InMemoryCache, IntrospectionFragmentMatcher } from 'apollo-cache-inmemory';
import { persistCache } from 'apollo-cache-persist';
import { ApolloClientOptions } from 'apollo-client';
import { ApolloLink } from 'apollo-link';
import { setContext } from 'apollo-link-context';
import gql from 'graphql-tag';
import { CurrentAuthQuery } from '../generated/graphql-types.js';
import schema from '../generated/graphql.schema.json'; // tslint:disable-line: no-default-import

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

  function getCurrentAuth() {
    // FIXME: should not require a try-catch, change approach.
    try {
      return (
        cache.readQuery<CurrentAuthQuery>({
          query: currentAuthQuery,
        }) ?? null
      );
    } catch {
      return null;
    }
  }

  const link = ApolloLink.from([
    setContext((operation, context) => {
      const token = getCurrentAuth()?.currentAuth?.token ?? null;

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
        currentAuth: getCurrentAuth,
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
