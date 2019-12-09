import gql from 'graphql-tag';

import { AwardFragment } from './__generated__/AwardFragment';
import { MaterialFragment } from './__generated__/MaterialFragment';
import { ProblemFragment } from './__generated__/ProblemFragment';
import { ProblemTacklingFragment } from './__generated__/ProblemTacklingFragment';
import { submissionAwardFragment } from './awards';
import { getAwardScoreRanges, getProblemScoreRange } from './material';

export const problemFragment = gql`
  fragment ProblemTacklingFragment on ProblemTackling {
    awards {
      ...SubmissionAwardFragment
      submission {
        id
      }
    }
    canSubmit
  }
  ${submissionAwardFragment}
`;

const getAwardValue = (awardName: string, tackling: ProblemTacklingFragment) =>
  tackling.awards.find((s) => s.awardName === awardName);

export const getAwardScore = (awardName: string, tackling: ProblemTacklingFragment) => {
  const result = getAwardValue(awardName, tackling);

  return result !== undefined && result.value.__typename === 'ScoreAwardValue' ? result.value.score : 0;
};

export const getAwardBadge = (awardName: string, tackling: ProblemTacklingFragment) => {
  const result = getAwardValue(awardName, tackling);

  return result !== undefined && result.value.__typename === 'BadgeAwardValue' ? result.value.badge : false;
};

export const getProblemScore = (material: MaterialFragment, tackling: ProblemTacklingFragment) =>
  getAwardScoreRanges(material)
    .map(({ name }) => getAwardScore(name, tackling))
    .reduce((a, b) => a + b, 0);

export const getProblemState = ({ material, tackling }: ProblemFragment) => ({
  award: ({ name, content }: AwardFragment) => ({
    score: tackling !== null ? getAwardScore(name, tackling) : undefined,
    badge: tackling !== null ? getAwardBadge(name, tackling) : undefined,
    range: content.__typename === 'ScoreAwardContent' ? content.range : undefined,
  }),
  range: getProblemScoreRange(material),
  score: tackling !== null ? getProblemScore(material, tackling) : undefined,
});
