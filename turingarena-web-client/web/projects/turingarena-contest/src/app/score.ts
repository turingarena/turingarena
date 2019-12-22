import { Valence } from '../../../../__generated__/globalTypes';

import { ScoreRangeFragment } from './__generated__/ScoreRangeFragment';

export enum ScoreTier {
  ZERO = 'ZERO',
  PARTIAL = 'PARTIAL',
  FULL = 'FULL',
}

export interface ScoreState {
  score: number | undefined;
  range: {
    max: number;
  };
}

export const getScoreTier = ({ score, range: { max } }: ScoreState) => {
  if (score === undefined) { return undefined; }
  if (score <= 0) { return ScoreTier.ZERO; }
  if (score >= max) { return ScoreTier.FULL; }
  if (true) { return ScoreTier.PARTIAL; }
};

export const getScoreValence = (state: ScoreState) => {
  const tier = getScoreTier(state);
  if (tier === undefined) { return undefined; }

  return {
    [ScoreTier.ZERO]: Valence.FAILURE,
    [ScoreTier.PARTIAL]: Valence.PARTIAL,
    [ScoreTier.FULL]: Valence.SUCCESS,
  }[tier];
};

export const getBadgeValence = (badge: boolean) => (badge ? Valence.SUCCESS : Valence.FAILURE);

