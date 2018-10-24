import * as React from 'react';
import './App.css';
import { observable, action, computed } from "mobx";
import { observer } from "mobx-react";
import { Client } from '@turingarena/client';

import AceEditor from 'react-ace';

import 'brace/mode/java';
import 'brace/mode/c_cpp';
import 'brace/theme/github';

const client: Client = new Client(
  process.env.TURINGARENA_ENDPOINT || "https://api.turingarena.org",
  "http://turingarena-branch-cloud-files-files.s3-website-us-east-1.amazonaws.com/",
);

const EvaluationView = observer(({ evaluation }) => (
  <React.Fragment>
    {evaluation.pending && <p>evaluating...</p>}
    {evaluation.resolved && <p>Evaluation complete!</p>}
    {evaluation.rejected && <p>An error occurred: {evaluation.error.message}</p>}
    <pre>
      {evaluation.textEvents.map(e => e.payload).join("")}
    </pre>
  </React.Fragment>
))

const currentEvaluation = observable.box();

export class Evaluation {
  @observable events = [];
  @observable resolved = false;
  @observable rejected = false;
  @observable error = null;

  constructor(events) {
    this.doLoad(events);
  }

  async doLoad(events) {
    try {
      for await (let event of events) {
        this.addEvent(event);
      }
      this.resolve();
    } catch (e) {
      this.reject(e);
    }
  }

  @computed
  get pending() {
    return !this.resolved && !this.rejected;
  }

  @computed
  get textEvents() {
    return this.events.filter(e => e.type === "text");
  }

  @action
  addEvent(e) {
    this.events.push(e);
  }

  @action
  resolve() {
    this.resolved = true;
  }

  @action
  reject(e) {
    this.rejected = true;
    this.error = e;
  }
}

@observer
export default class App extends React.Component<any> {
  editor = React.createRef();

  @action
  onSubmit(e) {
    e.preventDefault();
    const data = new FormData();

    data.append("packs[]", "d1a18623594c47621e9289767bc3ce997ce45756") // examples/sum_of_two_numbers
    data.append("evaluator_cmd", "/usr/local/bin/python -u evaluator.py")
    data.append("repositories[main][type]", "git_clone")
    data.append("repositories[main][url]", "https://github.com/turingarena/turingarena.git")
    data.append("submission[source]", new File([this.editor.current.editor.getValue()], "source.cpp"))

    currentEvaluation.set(new Evaluation(client.evaluate(data)));
  }

  componentDidMount() {
    this.editor.current.editor.setValue("int sum(int a, int b) {\n\treturn 0;\n}")
  }

  generate() {
    client.getFiles([
      "d1a18623594c47621e9289767bc3ce997ce45756"
    ], [
      "https://github.com/turingarena/turingarena.git"
    ]);
  }

  render() {
    return (
      <React.Fragment>
        <p>Write a function <code>sum</code> which accepts two integers and returns their sum.</p>
        <button onClick={() => this.generate()}>Generate</button>
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
