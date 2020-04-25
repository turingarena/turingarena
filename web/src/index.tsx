// tslint:disable: no-import-side-effect no-submodule-imports no-default-import
import { ApolloClient, ApolloProvider, concat, HttpLink, InMemoryCache } from '@apollo/client';
import { library } from '@fortawesome/fontawesome-svg-core';
import { fas } from '@fortawesome/free-solid-svg-icons';
import 'ag-grid-community/dist/styles/ag-grid.css';
import 'ag-grid-community/dist/styles/ag-theme-balham.css';
import 'bootstrap/dist/css/bootstrap.css';
import i18next from 'i18next';
import I18nextBrowserLanguageDetector from 'i18next-browser-languagedetector';
import 'katex/dist/katex.min.css';
import React from 'react';
import ReactDOM from 'react-dom';
import { initReactI18next } from 'react-i18next';
import { MainLoader } from './core/main-loader';
import result from './generated/possible-types';
import './index.css';
import { en } from './translations/en';
import { it } from './translations/it';
import { initAuthCache, readAuthCache } from './util/auth';

i18next
  .use(initReactI18next) // passes i18n down to react-i18next
  .use(I18nextBrowserLanguageDetector)
  .init({
    resources: { en, it },
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false,
    },
  })
  .catch(e => console.error(e));

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
        <MainLoader />
      </ApolloProvider>
    </React.StrictMode>
  );
}

ReactDOM.render(<App />, document.getElementById('root'));
