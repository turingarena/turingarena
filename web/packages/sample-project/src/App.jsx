import { Component } from 'react';
import './App.css';
import { Evaluation } from '@turingarena/evaluation';

const e = new Evaluation("a");

export default class App extends Component {
  state = {
    name: 'sample-project'
  };

  render() {
    return (
      <div className="App">
        <h1>Welcome to {this.state.name}</h1>
        {e.id}
      </div>
    );
  }
}
