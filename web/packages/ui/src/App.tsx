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

export default class App extends React.Component<any> {
  editor = React.createRef();

  constructor(props) {
    super(props);
    this.state = {
      events: [],
    };
  }

  async onSubmit(e) {
    e.preventDefault();
    const data = new FormData();

    data.append("oid", "d1a18623594c47621e9289767bc3ce997ce45756") // examples/sum_of_two_numbers
    data.append("repository[url]", "https://github.com/turingarena/turingarena.git")
    data.append("submission[source]", new File([this.editor.current.editor.getValue()], "source.cpp"))

    this.setState({events: []})
    for await(const e of client.evaluate(data)) {
      this.state.events.push(e);
      this.forceUpdate();
    }
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
        <pre>{this.state.events.filter(e => e.type == "text").map(e => e.payload).join("")}</pre>
      </React.Fragment>
    );
  }
}
