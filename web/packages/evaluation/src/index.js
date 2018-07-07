import { observable, action, computed } from "mobx";

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

export class Client {
  constructor(endpoint) {
    this.endpoint = endpoint;
  }

  async safeFetch(url, options) {
    const response = await fetch(url, options);
    if(!response.ok) {
      const { message } = await response.json();
      throw Error("API request failed: " + message);
    }
    return response;
  }

  async * evaluate(data) {
    const response = await this.safeFetch(this.endpoint + "evaluate", {
      method: 'POST',
      body: data,
    });
    const { id } = await response.json();

    yield *this.generateEvaluationEvents(id);
  }

  async loadEvaluationPage(id, after) {
    let afterOption;
    if(after) {
      afterOption = "&after=" + after;
    } else {
      afterOption = "";
    }
    const response = await this.safeFetch(this.endpoint +"evaluation_events?evaluation=" + id + afterOption);
    return await response.json();
  }

  async * generateEvaluationEvents(id) {
    let page = await this.loadEvaluationPage(id);

    yield *page.data;

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
      page = await this.loadEvaluationPage(id, page.end);
      yield *page.data;
    }
  }
}

export class Evaluation {
  @observable events = [];

  constructor(events) {
    this.doLoad(events).next();
  }

  async * doLoad(events) {
    // in a async * due to https://github.com/babel/babel/issues/4969
    for await (let event of events) {
      this.addEvent(event);
    }
  }

  @computed
  get textEvents() {
    return this.events.filter(e => e.type === "text");
  }

  @action
  addEvent(e) {
    this.events.push(e);
  }
}
