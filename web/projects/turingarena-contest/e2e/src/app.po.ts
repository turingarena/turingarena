// tslint:disable: no-floating-promises

// tslint:disable-next-line: no-implicit-dependencies
import { browser, by, element } from 'protractor';

export class AppPage {
  async navigateTo() {
    return browser.get(browser.baseUrl) as Promise<unknown>;
  }

  async getTitleText() {
    return element(by.css('app-root .content span')).getText() as Promise<string>;
  }
}
