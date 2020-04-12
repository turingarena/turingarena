import { ApolloClient, ApolloProvider, gql, HttpLink, InMemoryCache, useQuery } from '@apollo/client';
import React from 'react';

const client = new ApolloClient({
  cache: new InMemoryCache(),
  link: new HttpLink({
    uri: '/graphql',
  }),
});

export function MainView() {
  const { loading, error, data } = useQuery(gql`
    query Main {
      mainView(username: "user1") {
        user {
          id
        }
      }
    }
  `);

  if (loading) return <>Loading...</>;
  if (error !== undefined) return <>Error! {error.message}</>;

  return <div>{JSON.stringify(data)}</div>;
}

export function App() {
  return (
    <ApolloProvider client={client}>
      <div className="App">
        <h1>It works</h1>
      </div>
    </ApolloProvider>
  );
}
