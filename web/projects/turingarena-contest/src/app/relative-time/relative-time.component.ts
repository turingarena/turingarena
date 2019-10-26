import { Component, Inject, Input, LOCALE_ID, OnChanges } from '@angular/core';
import { DateTime } from 'luxon';
import { interval, Observable } from 'rxjs';
import { map, startWith } from 'rxjs/operators';

@Component({
  selector: 'app-relative-time',
  template: `<abbr [title]="time | date:'full'">{{ relativeTimeObservable | async }}</abbr>`,
})
export class RelativeTimeComponent implements OnChanges {
  constructor(@Inject(LOCALE_ID) private locale: string) { }

  @Input()
  time!: string;

  relativeTimeObservable: Observable<string>;

  ngOnChanges() {
    this.relativeTimeObservable = interval(10000).pipe(
      startWith([0]),
      map(() => {
        const time = DateTime.fromISO(this.time).setLocale(this.locale);
        return time.diffNow().as('seconds') > -10 ? 'now' : (time.toRelative() || '');
      }),
    )
  }
}
