export type ErrorMessageProvider = string | (() => string);

export function check(condition: boolean, message?: ErrorMessageProvider): asserts condition {
  if (!condition) fail(message);
}

export function unexpected(value: never): never {
  fail(() => `unexpected value ${value}`);
}

export function fail(message?: ErrorMessageProvider): never {
  throw new Error(typeof message === 'function' ? message() : message);
}
