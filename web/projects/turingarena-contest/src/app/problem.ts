import gql from 'graphql-tag';
import { getAwardScoreRanges, getProblemScoreRange } from './material';
import { AwardFragment } from './__generated__/AwardFragment';
import { MaterialFragment } from './__generated__/MaterialFragment';
import { ProblemTacklingFragment } from './__generated__/ProblemTacklingFragment';
import { ProblemFragment } from './__generated__/ProblemFragment';
import { TacklingFragment } from './__generated__/TacklingFragment';


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

export const getAwardScore = (awardName: string, tackling: TacklingFragment) => {
  const result = tackling.scores.find((s) => s.awardName === awardName);

  return result !== undefined ? result.score as number : 0;
};

export const getAwardBadge = (awardName: string, tackling: TacklingFragment) => {
  const result = tackling.badges.find((s) => s.awardName === awardName);

  return result !== undefined ? result.badge : false;
};

export const getProblemScore = (material: MaterialFragment, tackling: TacklingFragment) =>
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
