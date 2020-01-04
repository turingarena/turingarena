import gql from 'graphql-tag';

import { AwardFragment } from './__generated__/AwardFragment';
import { ProblemTacklingFragment } from './__generated__/ProblemTacklingFragment';
import { ProblemViewFragment } from './__generated__/ProblemViewFragment';
import { awardOutcomeFragment } from './awards';
import { problemMaterialFragment } from './material';
import { scoreRangeFragment } from './score';
import { submissionFragment } from './submission';

export const problemViewFragment = gql`
  fragment ProblemViewFragment on ProblemView {
    name
    tackling {
      ...ProblemTacklingFragment
      submissions { ...SubmissionFragment }
    }
    material { ...MaterialFragment }
    totalScoreRange { ...ScoreRangeFragment }
  }

  fragment ProblemTacklingFragment on ProblemTackling {
    awards {
      ...AwardOutcomeFragment
      submission {
        id
      }
    }
    totalScore
    canSubmit
  }

  ${problemMaterialFragment}
  ${submissionFragment}
  ${awardOutcomeFragment}
  ${scoreRangeFragment}
`;

const getAwardValue = (awardName: string, tackling: ProblemTacklingFragment) =>
  tackling.awards.find((s) => s.awardName === awardName);

const getAwardScore = (awardName: string, tackling: ProblemTacklingFragment) => {
  const result = getAwardValue(awardName, tackling);

  return result !== undefined && result.value.__typename === 'ScoreAwardValue' ? result.value.score : 0;
};

const getAwardBadge = (awardName: string, tackling: ProblemTacklingFragment) => {
  const result = getAwardValue(awardName, tackling);

  return result !== undefined && result.value.__typename === 'BadgeAwardValue' ? result.value.badge : false;
};

export const getProblemState = (problem: ProblemViewFragment) => ({
  award: ({ name, content }: AwardFragment) => ({
    score: problem.tackling !== null ? getAwardScore(name, problem.tackling) : undefined,
    badge: problem.tackling !== null ? getAwardBadge(name, problem.tackling) : undefined,
    range: content.__typename === 'ScoreAwardContent' ? content.range : undefined,
  }),
  range: problem.totalScoreRange,
  score: problem.tackling !== null ? problem.tackling.totalScore : undefined,
});
