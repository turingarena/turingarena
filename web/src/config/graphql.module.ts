import { NgModule } from '@angular/core';
import { APOLLO_OPTIONS, ApolloModule } from 'apollo-angular';
import { HttpLink, HttpLinkModule } from 'apollo-angular-link-http';
import { InMemoryCache, IntrospectionFragmentMatcher } from 'apollo-cache-inmemory';
import { ApolloClientOptions } from 'apollo-client';
import { ApolloLink } from 'apollo-link';
import { setContext } from 'apollo-link-context';
import schema from '../../../server/src/generated/graphql.schema.json'; // tslint:disable-line: no-default-import
import { AuthService } from '../util/auth.service.js';

const createApollo = (httpLink: HttpLink, authService: AuthService): ApolloClientOptions<unknown> => {
  const authContext = setContext((operation, context) => {
    const auth = authService.getAuth();

    return {
      headers: auth.token !== null ? { Authorization: `Bearer ${auth.token}` } : {},
    };
  });

  const link = ApolloLink.from([authContext, httpLink.create({ uri: '/graphql' })]);
  const cache = new InMemoryCache({
    fragmentMatcher: new IntrospectionFragmentMatcher({
      introspectionQueryResultData: schema,
    }),
    freezeResults: true,
    dataIdFromObject: () => undefined,
  });

  return {
    link,
    cache,
    resolvers: {
      Query: {},
    },
  };
};

@NgModule({
  exports: [ApolloModule, HttpLinkModule],
  providers: [
    {
      provide: APOLLO_OPTIONS,
      useFactory: createApollo,
      deps: [HttpLink, AuthService],
    },
  ],
})
export class GraphQLModule {}
