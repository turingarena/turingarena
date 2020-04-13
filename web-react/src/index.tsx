// tslint:disable: no-import-side-effect no-submodule-imports no-default-import
import { ApolloClient, ApolloProvider, concat, HttpLink, InMemoryCache } from '@apollo/client';
import { library } from '@fortawesome/fontawesome-svg-core';
import { fas } from '@fortawesome/free-solid-svg-icons';
import 'ag-grid-community/dist/styles/ag-grid.css';
import 'ag-grid-community/dist/styles/ag-theme-balham.css';
import 'katex/dist/katex.min.css';
import React from 'react';
import ReactDOM from 'react-dom';
import { CurrentAuthProvider, currentAuthQuery, initialCurrentAuthQueryData } from './core/current-auth';
import { MainLoader } from './core/main-loader';
import { CurrentAuthQuery, CurrentAuthQueryVariables } from './generated/graphql-types';
import result from './generated/possible-types';
import './index.css';

library.add(fas);

const cache = new InMemoryCache({ possibleTypes: result.possibleTypes });
cache.writeQuery<CurrentAuthQuery, CurrentAuthQueryVariables>({
  query: currentAuthQuery,
  data: initialCurrentAuthQueryData,
});

const client = new ApolloClient({
  cache,
  link: concat(
    (operation, forward) => {
      const data = cache.readQuery<CurrentAuthQuery, CurrentAuthQueryVariables>({ query: currentAuthQuery });
      const token = data?.currentToken ?? null;

      if (token !== null) {
        operation.setContext({ headers: { authorization: `Bearer ${token}` } });
      }

      return forward(operation);
    },
    new HttpLink({
      uri: '/graphql',
    }),
  ),
  resolvers: {}, // allow local queries
});

function App() {
  return (
    <React.StrictMode>
      <ApolloProvider client={client}>
        <CurrentAuthProvider component={currentAuth => <MainLoader currentAuth={currentAuth} />} />
      </ApolloProvider>
    </React.StrictMode>
  );
}

ReactDOM.render(<App />, document.getElementById('root'));
