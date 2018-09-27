const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

enum EvaluationEventType {
  TEXT = "text",
  DATA = "data",
}

interface EvaluationEvent {
  type: EvaluationEventType,
  payload: any,
}

interface BackoffConfig {
  initialBackoff: number;
  backoffFactor: number;
  maxBackoff: number;
  maxLimit: number;
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

  private async backoff(action: () => Promise<[boolean, any]>, config: BackoffConfig) {
    let staleCount = 0;
    let backoff = config.initialBackoff;

    while (true) {
      const [done, result] = await action();
      if (done) return result;

      await sleep(backoff);
      backoff *= config.backoffFactor;
      if (backoff > config.maxBackoff) {
        backoff = config.maxBackoff;
        staleCount++;
      }
      if (staleCount >= config.maxLimit) {
        throw new Error("backoff timeout");
      }
    }
  }

  private async * generateEvaluationEvents(id): AsyncIterable<EvaluationEvent> {
    const initialWait = 10000;
    const backoffConfig: BackoffConfig = {
      maxLimit: 10,
      initialBackoff: 100,
      backoffFactor: 2,
      maxBackoff: 3000,
    };

    await sleep(initialWait);

    let page = await this.loadEvaluationPage(id);

    yield* page.data;

    while (page.end) {
      page = await this.backoff(async () => {
        const myPage = await this.loadEvaluationPage(id, page.end);
        return [myPage.end !== myPage.start, myPage];
      }, backoffConfig);
      yield* page.data;
    }
  }
}
