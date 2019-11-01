import gql from 'graphql-tag';

import { ProblemMaterialFragment } from './__generated__/ProblemMaterialFragment';
import { ProblemTacklingFragment } from './__generated__/ProblemTacklingFragment';
import { scoreRanges } from './problem-material';

export const problemFragment = gql`
  fragment ProblemTacklingFragment on ProblemTackling {
    scores {
      awardName
      score
      submissionId
    }
    badges {
      awardName
      badge
      submissionId
    }
    canSubmit
  }
`;

export const getProblemState = (problem: ProblemMaterialFragment, tackling: ProblemTacklingFragment) => ({
  award: ({ name }: { name: string }) => ({
    score: 0,
    badge: false,
    ...tackling.scores.find((s) => s.awardName === name),
    ...tackling.badges.find((s) => s.awardName === name),
  }),
  maxScore: scoreRanges(problem).map(({ range: { max } }) => max).reduce((a: number, b: number) => a + b, 0),
  precision: scoreRanges(problem).map(({ range: { precision } }) => precision).reduce((a, b) => Math.max(a, b)),
  score: scoreRanges(problem)
    .map(({ name }) => tackling.scores.find((s) => s.awardName === name))
    .map((state) => ({ score: 0, ...state }))
    .map(({ score }) => score as number)
    .reduce((a, b) => a + b, 0),
});
