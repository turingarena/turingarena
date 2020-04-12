import React from 'react';
import './app.css'; // tslint:disable-line: no-import-side-effect
import { default as logo } from './logo.svg'; // tslint:disable-line: no-default-import

export function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.tsx</code> and save to reload.
        </p>
        <a className="App-link" href="https://reactjs.org" target="_blank" rel="noopener noreferrer">
          Learn React
        </a>
      </header>
    </div>
  );
}
