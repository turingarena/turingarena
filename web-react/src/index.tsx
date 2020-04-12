// tslint:disable: no-import-side-effect no-submodule-imports
import { ApolloClient, ApolloProvider, HttpLink, InMemoryCache } from '@apollo/client';
import { library } from '@fortawesome/fontawesome-svg-core';
import { fas } from '@fortawesome/free-solid-svg-icons';
import 'ag-grid-community/dist/styles/ag-grid.css';
import 'ag-grid-community/dist/styles/ag-theme-balham.css';
import React from 'react';
import ReactDOM from 'react-dom';
import { MainLoader } from './core/main-loader';
import './index.css';

library.add(fas);

const client = new ApolloClient({
  cache: new InMemoryCache(),
  link: new HttpLink({
    uri: '/graphql',
  }),
});

ReactDOM.render(
  <React.StrictMode>
    <ApolloProvider client={client}>
      <MainLoader />
    </ApolloProvider>
  </React.StrictMode>,
  document.getElementById('root'),
);
