import React from 'react';
import { observable, action, computed } from "mobx";
import { observer } from "mobx-react";
import ProblemView from './ProblemView';
import './App.css';

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

class Evaluation {
  @observable events = [];

  constructor(id) {
    this.id = id;
    this.load();
  }

  async loadPage(after) {
    let afterOption;
    if(after) {
      afterOption = "&after=" + after;
    } else {
      afterOption = "";
    }
    const response = await fetch(process.env.TURINGARENA_ENDPOINT +"evaluation_events?evaluation=" + this.id + afterOption);
    return await response.json();
  }

  async load() {
    let page = await this.loadPage();
    this.events.push(...page.data);
    
    const maxLimit = 10;
    const initialBackoff = 100;
    const maxBackoff = 3000;
    let staleCount = 0;
    let backoff = initialBackoff;
    while(page.end) {
      if(page.data.length > 0) {
        backoff = initialBackoff;
        staleCount = 0;
      } else {
        await sleep(backoff);
        backoff = backoff * 2;
        if(backoff > maxBackoff) {
          backoff = maxBackoff;
          staleCount++;
        }
        if(staleCount >= maxLimit) {
          break;
        }
      }
      page = await this.loadPage(page.end);
      this.events.push(...page.data);
    }
  }

  @computed
  get textEvents() {
    return this.events.filter(e => e.type === "text");
  }

  @action
  addEvent(e) {
    this.events.unshift(e);
  }
}

@observer
class AppView extends React.Component {
  render() {
    return (
      <pre>
        {this.props.evaluation.get() && this.props.evaluation.get().textEvents.map(e => e.payload).join("")}
      </pre>
    );
  }
}

const evaluation = observable.box();

const evaluate = () => {
  const data = new FormData()

  data.append("submission[source]", new File(["int sum(int a, int b) {return a+b;}"], "source.cpp"))
  data.append("packs[]", "d1a18623594c47621e9289767bc3ce997ce45756") // examples/sum_of_two_numbers
  data.append("evaluator_cmd", "/usr/local/bin/python -u evaluator.py")
  data.append("repositories[main][type]", "git_clone")
  data.append("repositories[main][url]", "https://github.com/turingarena/turingarena.git")

  fetch(process.env.TURINGARENA_ENDPOINT + "evaluate", {
    method: 'POST',
    body: data,
  }).then((response) => {
    return response.json();
  }).then((json) => {
    evaluation.set(new Evaluation(json.id));
  });
}

export default () => (
  <div>
    <button onClick={() => evaluate()}>Evaluate</button>
    <AppView evaluation={evaluation} />
  </div>
);
