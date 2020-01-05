import gql from 'graphql-tag';

import { Valence } from '../../../../../__generated__/globalTypes';

import { ScoreAwardGradingFragment } from './__generated__/ScoreAwardGradingFragment';

export const scoreRangeFragment = gql`
  fragment ScoreRangeFragment on ScoreRange {
    max
    precision
  }
`;

export enum ScoreTier {
  ZERO = 'ZERO',
  PARTIAL = 'PARTIAL',
  FULL = 'FULL',
}

export const getScoreTier = ({ grade, domain: { range: { max } } }: ScoreAwardGradingFragment) => {
  if (grade === null) { return undefined; }
  const { value: { score } } = grade;
  if (score <= 0) { return ScoreTier.ZERO; }
  if (score >= max) { return ScoreTier.FULL; }
  if (true) { return ScoreTier.PARTIAL; }
};

export const getScoreValence = (grading: ScoreAwardGradingFragment) => {
  const tier = getScoreTier(grading);
  if (tier === undefined) { return undefined; }

  return {
    [ScoreTier.ZERO]: Valence.FAILURE,
    [ScoreTier.PARTIAL]: Valence.PARTIAL,
    [ScoreTier.FULL]: Valence.SUCCESS,
  }[tier];
};

export const getBadgeValence = (badge: boolean) => (badge ? Valence.SUCCESS : Valence.FAILURE);
