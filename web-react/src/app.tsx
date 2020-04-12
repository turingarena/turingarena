import { ApolloClient, ApolloProvider, gql, HttpLink, InMemoryCache, useQuery } from '@apollo/client';
import React from 'react';
import './app.css'; // tslint:disable-line: no-import-side-effect
import { default as logo } from './logo.svg'; // tslint:disable-line: no-default-import

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
        <header className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <MainView></MainView>
          <p>
            Edit <code>src/App.tsx</code> and save to reload.
          </p>
          <a className="App-link" href="https://reactjs.org" target="_blank" rel="noopener noreferrer">
            Learn React
          </a>
        </header>
      </div>
    </ApolloProvider>
  );
}
