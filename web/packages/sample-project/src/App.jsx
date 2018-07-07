import React from 'react';
import './App.css';
import { observer } from "mobx-react";
import { Client, Evaluation } from '@turingarena/evaluation';

const client = new Client("https://api.turingarena.org/");

const data = new FormData()

data.append("submission[source]", new File(["int sum(int a, int b) {return a+b;}"], "source.cpp"))
data.append("packs[]", "d1a18623594c47621e9289767bc3ce997ce45756") // examples/sum_of_two_numbers
data.append("evaluator_cmd", "/usr/local/bin/python -u evaluator.py")
data.append("repositories[main][type]", "git_clone")
data.append("repositories[main][url]", "https://github.com/turingarena/turingarena.git")

const evaluation = new Evaluation(client.evaluate(data));

@observer
class EvaluationView extends React.Component {
  render() {
    return (
      <pre>
        {evaluation.textEvents.map(e => e.payload).join("")}
      </pre>
    );
  }
}

export default class App extends React.Component {
  render() {
    return (
      <EvaluationView />
    );
  }
}
