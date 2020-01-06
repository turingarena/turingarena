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
  transform<T, U>(value: T, f: (arg: T) => U): U {
    console.log(`applyPure`, f, value);

    return f(value);
  }
}
