import { AwardGradingFragment } from '../fragments/__generated__/AwardGradingFragment';
import { getScoreTier } from '../fragments/score';

export const gradingAttributes: Array<[string, (grading: AwardGradingFragment) => string | undefined]> = [
  ['data-grading-typename', grading => grading.__typename],
  [
    'data-score-tier',
    grading => {
      if (grading.__typename === 'ScoreAwardGrading') {
        return getScoreTier(grading);
      }
    },
  ],
  [
    'data-badge',
    grading => {
      if (grading.__typename === 'BadgeAwardGrading') {
        const { grade } = grading;

        return grade !== null ? `${grade.value.badge}` : undefined;
      }
    },
  ],
];
