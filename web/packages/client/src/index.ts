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
  private readonly filesEndpoint: string;

  constructor(endpoint, filesEndpoint) {
    this.endpoint = endpoint;
    this.filesEndpoint = filesEndpoint;
  }

  async * evaluate(data) {
    const response = await this.safeFetch(this.endpoint + "evaluate", {
      method: 'POST',
      body: data,
    });
    const { id } = await response.json();

    yield* this.generateEvaluationEvents(id);
  }

  async getFiles(layers, repositories) {
    const ans = await this.doGetFiles(layers);
    if (ans === undefined) {
      await this.generateFiles(layers, repositories);
      return await this.backoff(async () => {
        const data = await this.doGetFiles(layers);
        return [data !== undefined, data];
      }, {
        initialBackoff: 1000,
        backoffFactor: 2,
        maxBackoff: 5,
        maxLimit: 2,
      })
    }
  }

  private async doGetFiles(layers) {
    const response = await fetch(this.filesEndpoint + layers.join("_") + ".json")
    if (response.ok) return await response.json();
    return undefined;
  }

  private async generateFiles(layers: string[], repositories) {
    const data = new FormData();

    // TODO: define types for WorkingDirectory
    layers.map(l => data.append("packs[]", l));
    repositories.map((r, i) => {
      data.append(`repositories[${i}][type]`, "git_clone");
      data.append(`repositories[${i}][url]`, r);
    });

    await this.safeFetch(this.endpoint + "generate_file", {
      method: 'POST',
      body: data,
    });
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
