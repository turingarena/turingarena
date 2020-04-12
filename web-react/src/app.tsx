import { ApolloClient, ApolloProvider, HttpLink, InMemoryCache } from '@apollo/client';
import React from 'react';
import './app.css'; // tslint:disable-line: no-import-side-effect
import { MainLoader } from './core/main-loader';

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
