import { ApolloClient, ApolloProvider, HttpLink, InMemoryCache } from '@apollo/client';
import React from 'react';
import { MainLoader } from './main-loader';

const client = new ApolloClient({
  cache: new InMemoryCache(),
  link: new HttpLink({
    uri: '/graphql',
  }),
});

export function App() {
  return (
    <ApolloProvider client={client}>
      <MainLoader />
    </ApolloProvider>
  );
}
