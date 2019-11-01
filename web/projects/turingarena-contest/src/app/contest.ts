import gql from 'graphql-tag';
import { DateTime } from 'luxon';
import { interval } from 'rxjs';
import { map, startWith } from 'rxjs/operators';

import { ContestViewFragment } from './__generated__/ContestViewFragment';
import { getProblemState, problemFragment } from './problem';
import { problemMaterialFragment } from './problem-material';
import { submissionFragment } from './submission';

export const contestViewFragment = gql`
  fragment ContestViewFragment on ContestView {
    user {
      id
      displayName
    }
    contestTitle
    startTime
    endTime
    problems {
      name
      tackling {
        ...ProblemTacklingFragment
        submissions { ...SubmissionFragment }
      }
      ...ProblemMaterialFragment
    }
  }
  ${problemFragment}
  ${problemMaterialFragment}
  ${submissionFragment}
`;

export const getContestState = (contestView: ContestViewFragment) => {
  const { startTime, endTime, problems } = contestView;

  const problemTacklings = problems !== null ? problems.map((problem) => {
    const { tackling } = problem;
    if (tackling !== null) {
      return getProblemState(problem, tackling);
    } else {
      return {
        score: 0,
        range: {
          max: 0,
          precision: 0,
        },
      };
    }
  }) : [];

  return {
    hasScore: problems !== null && problems.some(({ tackling }) => tackling !== null),
    score: problemTacklings.map((s) => s.score).reduce((a, b) => a + b, 0),
    range: {
      max: problemTacklings.map((s) => s.range.max as number).reduce((a, b) => a + b, 0),
      precision: problemTacklings.map((s) => s.range.precision).reduce((a, b) => Math.max(a, b), 0),
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
