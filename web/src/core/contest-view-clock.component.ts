import { Component, Input } from '@angular/core';
import gql from 'graphql-tag';
import { DateTime, Duration } from 'luxon';
import { interval } from 'rxjs';
import { map, startWith } from 'rxjs/operators';
import { ContestViewClockFragment } from '../generated/graphql-types';

@Component({
  selector: 'app-contest-view-clock',
  templateUrl: './contest-view-clock.component.html',
  styleUrls: ['./contest-view-clock.component.scss'],
})
export class ContestViewClockComponent {
  @Input()
  data!: ContestViewClockFragment;

  clock = interval(Duration.fromObject({ seconds: 1 }).as('milliseconds')).pipe(
    startWith(0),
    map(() => {
      const now = DateTime.local();
      const start = DateTime.fromISO(this.data.contest.start);
      const end = DateTime.fromISO(this.data.contest.end);

      switch (this.data.contest.status) {
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

export const contestViewClockFragment = gql`
  fragment ContestViewClock on ContestView {
    contest {
      start
      end
      status
    }
  }
`;
