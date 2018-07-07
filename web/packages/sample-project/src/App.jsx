import React from 'react';
import './App.css';
import { observable, action } from "mobx";
import { observer } from "mobx-react";
import { Client, Evaluation } from '@turingarena/evaluation';

const client = new Client("https://api.turingarena.org/");

@observer
class EvaluationView extends React.Component {
  render() {
    const evaluation = this.props.evaluation;
    return (
      <React.Fragment>
        {evaluation.pending && <p>evaluating...</p>}
        {evaluation.resolved && <p>Evaluation complete!</p>}
        {evaluation.rejected && <p>An error occurred: {evaluation.error.message}</p>}
        <pre>
          {evaluation.textEvents.map(e => e.payload).join("")}
        </pre>
      </React.Fragment>
    );
  }
}

const currentEvaluation = observable.box();

@observer
export default class App extends React.Component {
  @action
  onSubmit(e) {
    e.preventDefault();
    const data = new FormData(e.target);
    data.append("packs[]", "d1a18623594c47621e9289767bc3ce997ce45756") // examples/sum_of_two_numbers
    data.append("evaluator_cmd", "/usr/local/bin/python -u evaluator.py")
    data.append("repositories[main][type]", "git_clone")
    data.append("repositories[main][url]", "https://github.com/turingarena/turingarena.git")

    currentEvaluation.set(new Evaluation(client.evaluate(data)));
  }

  render() {
    return (
      <React.Fragment>
        <p>Write a function <code>sum</code> which accepts two integers and returns their sum.</p>
        <form onSubmit={(e) => this.onSubmit(e)}>
          <input type="file" name="submission[source]" />
          <input type="submit" />
        </form>
        {currentEvaluation.get() && <EvaluationView evaluation={currentEvaluation.get()} />}
      </React.Fragment>
    );
  }
}
