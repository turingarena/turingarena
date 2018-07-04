import React from 'react';
import { observable, action, computed } from "mobx";
import { observer } from "mobx-react";
import ProblemView from './ProblemView';
import './App.css';

class Evaluation {
  @observable events = [];
  @observable count = 3;

  @action
  addEvent(e) {
    this.count += 1;
    this.events.unshift(e);
  }
}

@observer
class AppView extends React.Component {
  render() {
    return (
      <div>
        {this.props.evaluation.count}
        <ul>
          {this.props.evaluation.events.map((event, i) =>
            <li key={i}>{event}</li>
          )}
        </ul>
      </div>
    );
  }
}

const evaluation = new Evaluation();

fetch("/").then(() => {
  evaluation.addEvent("ok");
})

export default () => (
  <div>
    <AppView evaluation={evaluation} />
  </div>
);
