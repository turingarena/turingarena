import gql from 'graphql-tag';
import { DateTime } from 'luxon';
import { interval } from 'rxjs';
import { map, startWith } from 'rxjs/operators';

import { ContestViewFragment } from './__generated__/ContestViewFragment';
import { fileFragment } from './file';
import { problemViewFragment } from './problem';
import { scoreRangeFragment } from './score';
import { textFragment } from './text';

export const contestViewFragment = gql`
  fragment ContestViewFragment on ContestView {
    user { ...UserFragment }
    home { ...FileFragment }
    title { ...TextFragment }
    startTime
    endTime
    problems { ...ProblemViewFragment }
    totalScoreRange { ...ScoreRangeFragment }
    totalScore
  }

  fragment UserFragment on User {
    id
    displayName
  }

  ${problemViewFragment}
  ${textFragment}
  ${fileFragment}
  ${scoreRangeFragment}
`;

export const getContestState = ({ startTime, endTime, totalScoreRange, totalScore }: ContestViewFragment) => ({
  hasScore: totalScore !== null,
  score: totalScore,
  range: totalScoreRange,
  // tslint:disable-next-line: no-magic-numbers
  clock: interval(1000).pipe(
    startWith(0),
    map(() => {
      const now = DateTime.local();
      const start = DateTime.fromISO(startTime);
      const end = DateTime.fromISO(endTime);

      return now < start
        ? {
          status: 'startingIn',
          value: start.diff(now),
        }
        : now < end
          ? {
            status: 'endingIn',
            value: end.diff(now),
          }
          : {
            status: 'endedBy',
            value: now.diff(end),
          };
    }),
  ),
});
