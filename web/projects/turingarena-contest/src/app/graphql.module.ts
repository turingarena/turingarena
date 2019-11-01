import { NgModule } from '@angular/core';
import { APOLLO_OPTIONS, ApolloModule } from 'apollo-angular';
import { HttpLink, HttpLinkModule } from 'apollo-angular-link-http';
import { InMemoryCache, IntrospectionFragmentMatcher } from 'apollo-cache-inmemory';
import { ApolloLink } from 'apollo-link';
import { setContext } from 'apollo-link-context';

// tslint:disable-next-line: no-default-import
import schema from '../../../../__generated__/graphql-schema.json';

import { getAuth } from './auth';

const createApollo = (httpLink: HttpLink) => {
  const authContext = setContext((operation, context) => {
    const auth = getAuth();

    return {
      headers: auth !== undefined ? {
        Authorization: auth.token,
      } : {},
    };
  });

  return {
    link: ApolloLink.from([authContext, httpLink.create({
      uri: window.location.toString() === 'http://localhost:4200/' ? 'http://localhost:8080/graphql' : '/graphql',
    })]),
    cache: new InMemoryCache({
      fragmentMatcher: new IntrospectionFragmentMatcher({
        introspectionQueryResultData: schema,
      }),
    }),
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
export class GraphQLModule { }
