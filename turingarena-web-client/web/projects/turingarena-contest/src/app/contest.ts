import gql from 'graphql-tag';
import { DateTime, Duration } from 'luxon';
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
