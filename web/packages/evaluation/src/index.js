import { observable, action, computed } from "mobx";

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

export class Evaluation {
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
