import gql from 'graphql-tag';
import { DateTime } from 'luxon';
import { interval } from 'rxjs';
import { map, startWith } from 'rxjs/operators';

import { ContestViewFragment } from './__generated__/ContestViewFragment';
import { fileFragment } from './file';
import { problemMaterialFragment } from './material';
import { getProblemState, problemFragment } from './problem';
import { submissionFragment } from './submission';
import { textFragment } from './text';

export const contestViewFragment = gql`
  fragment ContestViewFragment on ContestView {
    user { ...UserFragment }
    home { ...FileFragment }
    title { ...TextFragment }
    startTime
    endTime
    problems { ...ProblemFragment }
  }

  fragment UserFragment on User {
    id
    displayName
  }

  fragment ProblemFragment on ProblemView {
    name
    tackling {
      ...ProblemTacklingFragment
      submissions { ...SubmissionFragment }
    }
    material { ...MaterialFragment }
  }

  ${problemFragment}
  ${problemMaterialFragment}
  ${submissionFragment}
  ${textFragment}
  ${fileFragment}
`;

export const getContestState = (contestView: ContestViewFragment) => {
  const { startTime, endTime, problems } = contestView;
  const problemStates = problems !== null ? problems.map(getProblemState) : [];

  return {
    hasScore: problems !== null && problems.some(({ tackling }) => tackling !== null),
    score: problemStates.map(({ score = 0 }) => score).reduce((a, b) => a + b, 0),
    range: {
      max: problemStates.map(({ range: { max } }) => max).reduce((a, b) => a + b, 0),
      precision: problemStates.map(({ range: { precision } }) => precision).reduce((a, b) => Math.max(a, b), 0),
    },
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
  };
};
