import { gql } from '@apollo/client';
import { DateTime, Duration } from 'luxon';
import React from 'react';
import { interval } from 'rxjs';
import { useObservable } from 'rxjs-hooks';
import { map, startWith } from 'rxjs/operators';
import styled, { css } from 'styled-components';
import { ContestStatus, ContestViewClockFragment } from '../generated/graphql-types';
import { unexpected } from '../util/check';

export const contestViewClockFragment = gql`
  fragment ContestViewClock on ContestView {
    contest {
      start {
        local
      }
      end {
        local
      }
      status
    }
  }
`;

const ContestClock = styled.div<{ status: ContestStatus }>`
  font-family: 'Lucida Console', Monaco, monospace;
  font-size: 2rem;
  text-align: right;
  margin-bottom: 16px;

  ${({ status }) =>
    status === 'ENDED' &&
    css`
      /* TODO */
      /* @extend .text-danger; */
    `}
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

// TODO: duplicated?
const AsideHeader = styled.h2`
  text-transform: uppercase;
  font-size: 1.25rem;
  margin: 0 0 0.5rem;
  font-weight: 500;
  line-height: 1.2;
`;

export function ContestViewClock({ data }: { data: ContestViewClockFragment }) {
  const clock = useObservable(() =>
    interval(Duration.fromObject({ seconds: 1 }).as('milliseconds')).pipe(
      startWith(0),
      map(() => {
        const now = DateTime.local();
        const start = DateTime.fromISO(data.contest.start.local);
        const end = DateTime.fromISO(data.contest.end.local);

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
      <AsideHeader>{getContestStatus(data.contest.status)}</AsideHeader>

      {clock !== null && (
        <ContestClock status={data.contest.status}>
          {clock.negated ? '-' : ''}
          {clock.duration.toFormat('hh:mm:ss')}
        </ContestClock>
      )}
    </div>
  );
}
