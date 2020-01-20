import { Pipe, PipeTransform } from '@angular/core';

/**
 * Wraps any given (pure) function into a pure pipe.
 * (Pure pipes can improve performances.)
 */
@Pipe({
  name: 'applyPure',
  pure: true,
})
export class ApplyPurePipe implements PipeTransform {
  transform<T, U, X extends unknown[]>(value: T, f: (arg: T, ...rest: X) => U, ...rest: X): U {
    return f(value, ...rest);
  }
}
