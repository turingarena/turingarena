const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

enum EvaluationEventType {
  TEXT = "text",
  DATA = "data",
}

interface EvaluationEvent {
  type: EvaluationEventType,
  payload: any,
}

export class Client {
  private readonly endpoint: string;

  constructor(endpoint) {
    this.endpoint = endpoint;
  }

  async * evaluate(data) {
    const response = await this.safeFetch(this.endpoint + "evaluate", {
      method: 'POST',
      body: data,
    });
    const { id } = await response.json();

    yield* this.generateEvaluationEvents(id);
  }

  private async safeFetch(url, options = {}) {
    const response = await fetch(url, options);
    if (!response.ok) {
      const { message } = await response.json();
      throw Error("API request failed: " + message);
    }
    return response;
  }

  private async loadEvaluationPage(id, after = null) {
    let afterOption;
    if (after) {
      afterOption = "&after=" + after;
    } else {
      afterOption = "";
    }
    const response = await this.safeFetch(this.endpoint + "evaluation_events?evaluation=" + id + afterOption);
    return await response.json();
  }

  private async * generateEvaluationEvents(id): AsyncIterable<EvaluationEvent> {
    const initialWait = 10000;
    const maxLimit = 10;
    const initialBackoff = 100;
    const maxBackoff = 3000;

    await sleep(initialWait);

    let page = await this.loadEvaluationPage(id);

    yield* page.data;

    let staleCount = 0;
    let backoff = initialBackoff;
    while (page.end) {
      if (page.data.length > 0) {
        backoff = initialBackoff;
        staleCount = 0;
      } else {
        await sleep(backoff);
        backoff = backoff * 2;
        if (backoff > maxBackoff) {
          backoff = maxBackoff;
          staleCount++;
        }
        if (staleCount >= maxLimit) {
          throw new Error("timeout when fetching events");
        }
      }
      page = await this.loadEvaluationPage(id, page.end);
      yield* page.data;
    }
  }
}
