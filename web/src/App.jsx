import { Component } from 'preact';
import './App.css';

export default class App extends Component {
  state = {
    name: 'web',
  };

  render() {
    return (
      <div className="App">
        <h1>Welcome to {this.state.name}</h1>
      </div>
    );
  }
}
