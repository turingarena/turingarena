import { Valence } from '../../../../__generated__/globalTypes';

import { ScoreRangeFragment } from './__generated__/ScoreRangeFragment';

export enum ScoreTier {
  ZERO = 'ZERO',
  PARTIAL = 'PARTIAL',
  FULL = 'FULL',
}

export interface ScoreState {
  score: number;
  range: ScoreRangeFragment;
}

export const getScoreTier = ({ score, range: { max } }: ScoreState) =>
  score >= max
    ? ScoreTier.FULL
    : score <= 0
      ? ScoreTier.ZERO
      : ScoreTier.PARTIAL;

export const getScoreValence = (state: ScoreState) => ({
  [ScoreTier.ZERO]: Valence.FAILURE,
  [ScoreTier.PARTIAL]: Valence.PARTIAL,
  [ScoreTier.FULL]: Valence.SUCCESS,
}[getScoreTier(state)]);

export const getBadgeValence = (badge: boolean) => (badge ? Valence.SUCCESS : Valence.FAILURE);

