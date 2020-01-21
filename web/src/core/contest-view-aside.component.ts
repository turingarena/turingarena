import { Component, Input } from '@angular/core';
import { DateTime, Duration } from 'luxon';
import { interval } from 'rxjs';
import { map, startWith } from 'rxjs/operators';
import { ContestViewFragment } from '../generated/graphql-types';

@Component({
  selector: 'app-contest-view-aside',
  templateUrl: './contest-view-aside.component.html',
  styleUrls: ['./contest-view-aside.component.scss'],
})
export class ContestViewAsideComponent {
  @Input()
  data!: ContestViewFragment;

  getContestClock = ({ contest: { status, start: startIso, end: endIso } }: ContestViewFragment) =>
    interval(Duration.fromObject({ seconds: 1 }).as('milliseconds')).pipe(
      startWith(0),
      map(() => {
        const now = DateTime.local();
        const start = DateTime.fromISO(startIso);
        const end = DateTime.fromISO(endIso);

        switch (status) {
          case 'NOT_STARTED':
            return start.diff(now);
          case 'RUNNING':
            return end.diff(now);
          case 'ENDED':
            return now.diff(end);
          default:
            throw new Error();
        }
      }),
      map(duration =>
        duration.valueOf() >= 0
          ? {
              duration,
              negated: false,
            }
          : {
              duration: duration.negate(),
              negated: true,
            },
      ),
    );
}
