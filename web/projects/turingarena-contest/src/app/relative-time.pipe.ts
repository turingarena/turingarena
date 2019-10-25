import { Pipe, PipeTransform, LOCALE_ID, Inject } from '@angular/core';
import { DateTime } from 'luxon';

@Pipe({
  name: 'relativeTime'
})
export class RelativeTimePipe implements PipeTransform {
  constructor(@Inject(LOCALE_ID) private locale: string) { }

  transform(value: string): string {
    return DateTime.fromISO(value).setLocale(this.locale).toRelative() || '';
  }
}
