import gql from 'graphql-tag';
import { ScoreAwardGradingFragment, Valence } from '../../generated/graphql-types';

export const scoreRangeFragment = gql`
  fragment ScoreRangeFragment on ScoreRange {
    max
    precision
  }
`;

export type ScoreTier = 'zero' | 'partial' | 'full';

export const getScoreTier = ({
  grade,
  domain: {
    range: { max },
  },
}: ScoreAwardGradingFragment): ScoreTier | undefined => {
  if (grade === null) {
    return undefined;
  }
  const {
    value: { score },
  } = grade;
  if (score <= 0) {
    return 'zero';
  }
  if (score >= max) {
    return 'full';
  }
  if (true) {
    return 'partial';
  }
};

export const getScoreValence = (grading: ScoreAwardGradingFragment) => {
  const tier = getScoreTier(grading);
  if (tier === undefined) {
    return undefined;
  }

  return {
    zero: Valence.FAILURE,
    partial: Valence.PARTIAL,
    full: Valence.SUCCESS,
  }[tier];
};

export const getBadgeValence = (badge: boolean) => (badge ? Valence.SUCCESS : Valence.FAILURE);
