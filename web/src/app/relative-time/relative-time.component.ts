import { Component, Inject, Input, LOCALE_ID, OnChanges } from '@angular/core';
import { DateTime } from 'luxon';
import { interval, Observable } from 'rxjs';
import { map, startWith } from 'rxjs/operators';

@Component({
  selector: 'app-relative-time',
  template: `
    <abbr [title]="time | date: 'full'">{{ relativeTimeObservable | async }}</abbr>
  `,
})
export class RelativeTimeComponent implements OnChanges {
  constructor(@Inject(LOCALE_ID) private readonly locale: string) {}

  @Input()
  time!: string;

  relativeTimeObservable!: Observable<string>;

  ngOnChanges() {
    const time = DateTime.fromISO(this.time).setLocale(this.locale);

    const refreshInterval = 10000;
    const nowToleranceSeconds = 10;

    this.relativeTimeObservable = interval(refreshInterval).pipe(
      startWith(0),
      map(() => (time.diffNow().as('seconds') > -nowToleranceSeconds ? 'now' : time.toRelative()!)),
    );
  }
}
