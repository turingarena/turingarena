// tslint:disable: no-import-side-effect no-submodule-imports no-default-import
import { ApolloClient, ApolloProvider, concat, HttpLink, InMemoryCache } from '@apollo/client';
import { library } from '@fortawesome/fontawesome-svg-core';
import { fas } from '@fortawesome/free-solid-svg-icons';
import 'ag-grid-community/dist/styles/ag-grid.css';
import 'ag-grid-community/dist/styles/ag-theme-balham.css';
import 'bootstrap/dist/css/bootstrap.css';
import 'katex/dist/katex.min.css';
import React from 'react';
import ReactDOM from 'react-dom';
import { MainLoader } from './core/main-loader';
import result from './generated/possible-types';
import './index.css';
import { initAuthCache, readAuthCache } from './util/auth';
import { AppIntlProvider } from './util/intl';

library.add(fas);

const cache = new InMemoryCache({ possibleTypes: result.possibleTypes });

initAuthCache(cache);

const client = new ApolloClient({
  cache,
  link: concat(
    (operation, forward) => {
      const data = readAuthCache(cache);
      const token = data?.currentAuth?.token ?? null;

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
        <AppIntlProvider>
          <MainLoader />
        </AppIntlProvider>
      </ApolloProvider>
    </React.StrictMode>
  );
}

ReactDOM.render(<App />, document.getElementById('root'));
