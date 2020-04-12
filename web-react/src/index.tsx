import React from 'react';
import ReactDOM from 'react-dom';
import { App } from './core/app';
import './index.css'; // tslint:disable-line: no-import-side-effect

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root'),
);
