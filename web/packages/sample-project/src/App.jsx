import React from 'react';
import './App.css';
import { observable, action } from "mobx";
import { observer } from "mobx-react";
import { Client, Evaluation } from '@turingarena/evaluation';

import brace from 'brace';
import AceEditor from 'react-ace';

import 'brace/mode/java';
import 'brace/mode/c_cpp';
import 'brace/theme/github';

const client = new Client(process.env.TURINGARENA_ENDPOINT || "https://api.turingarena.org/");

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
const source = observable.box("");

@observer
export default class App extends React.Component {
  editor = React.createRef();

  @action
  onSubmit(e) {
    e.preventDefault();
    const data = new FormData();

    data.append("oid", "d1a18623594c47621e9289767bc3ce997ce45756") // examples/sum_of_two_numbers
    data.append("repository[url]", "https://github.com/turingarena/turingarena.git")
    data.append("submission[source]", new File([this.editor.current.editor.getValue()], "source.cpp"))

    currentEvaluation.set(new Evaluation(client.evaluate(data)));
  }

  componentDidMount() {
    this.editor.current.editor.setValue("int sum(int a, int b) {\n\treturn 0;\n}")
  }

  render() {
    return (
      <React.Fragment>
        <p>Write a function <code>sum</code> which accepts two integers and returns their sum.</p>
        <form onSubmit={(e) => this.onSubmit(e)}>
          {/*<input type="file" name="submission[source]" />*/}
          <input type="submit" />
        </form>
        <AceEditor
          theme="github"
          height="40vh"
          ref={this.editor}
          mode="c_cpp"
        />
        {currentEvaluation.get() && <EvaluationView evaluation={currentEvaluation.get()} />}
      </React.Fragment>
    );
  }
}
