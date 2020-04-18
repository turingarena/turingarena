import { gql } from '@apollo/client';
import { css } from 'emotion';
import { DateTime, Duration } from 'luxon';
import React from 'react';
import { interval } from 'rxjs';
import { useObservable } from 'rxjs-hooks';
import { map, startWith } from 'rxjs/operators';
import { ContestStatus, ContestViewClockFragment } from '../generated/graphql-types';
import { unexpected } from '../util/check';

export const contestViewClockFragment = gql`
  fragment ContestViewClock on ContestView {
    contest {
      start
      end
      status
    }
  }
`;

const getContestStatus = (status: ContestStatus) => {
  switch (status) {
    case 'NOT_STARTED':
      return 'Starting In';
    case 'RUNNING':
      return 'Remaining Time';
    case 'ENDED':
      return 'Ended';
    default:
      return unexpected(status);
  }
};

export function ContestViewClock({ data }: { data: ContestViewClockFragment }) {
  const clock = useObservable(() =>
    interval(Duration.fromObject({ seconds: 1 }).as('milliseconds')).pipe(
      startWith(0),
      map(() => {
        const now = DateTime.local();
        const start = DateTime.fromISO(data.contest.start);
        const end = DateTime.fromISO(data.contest.end);

        switch (data.contest.status) {
          case 'NOT_STARTED':
            return start.diff(now);
          case 'RUNNING':
            return end.diff(now);
          case 'ENDED':
            return now.diff(end);
          default:
            return unexpected(data.contest.status);
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
    ),
  );

  return (
    <div>
      <div
        className={css`
          text-transform: uppercase;
          font-size: 1.25rem;
          margin: 0 0 0.5rem;
          font-weight: 500;
          line-height: 1.2;
        `}
      >
        {getContestStatus(data.contest.status)}
      </div>

      {clock !== null && (
        <div
          className={css`
            font-family: 'Lucida Console', Monaco, monospace;
            font-size: 2rem;
            text-align: right;
            margin-bottom: 16px;
          `}
        >
          {clock.negated ? '-' : ''}
          {clock.duration.toFormat('hh:mm:ss')}
        </div>
      )}
    </div>
  );
}
