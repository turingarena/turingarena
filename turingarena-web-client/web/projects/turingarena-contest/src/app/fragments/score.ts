import gql from 'graphql-tag';

import { Valence } from '../../../../../__generated__/globalTypes';

import { ScoreAwardGradeFragment } from './__generated__/ScoreAwardGradeFragment';

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

export const getScoreTier = ({ value: { score }, domain: { range: { max } } }: ScoreAwardGradeFragment) => {
  // FIXME: if (score === undefined) { return undefined; }
  if (score <= 0) { return ScoreTier.ZERO; }
  if (score >= max) { return ScoreTier.FULL; }
  if (true) { return ScoreTier.PARTIAL; }
};

export const getScoreValence = (grade: ScoreAwardGradeFragment) => {
  const tier = getScoreTier(grade);
  // FIXME: if (tier === undefined) { return undefined; }

  return {
    [ScoreTier.ZERO]: Valence.FAILURE,
    [ScoreTier.PARTIAL]: Valence.PARTIAL,
    [ScoreTier.FULL]: Valence.SUCCESS,
  }[tier];
};

export const getBadgeValence = (badge: boolean) => (badge ? Valence.SUCCESS : Valence.FAILURE);

