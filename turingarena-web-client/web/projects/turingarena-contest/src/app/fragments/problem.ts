import gql from 'graphql-tag';

import { awardAchievementFragment, awardMaterialFragment, scoreAwardGradeFragment } from './awards';
import { problemMaterialFragment } from './material';
import { scoreRangeFragment } from './score';
import { submissionFragment } from './submission';

export const problemFragment = gql`
  fragment ProblemFragment on Problem {
    name
    material {
      ...MaterialFragment
    }
    totalScoreRange {
      ...ScoreRangeFragment
    }
  }

  ${problemMaterialFragment}
  ${scoreRangeFragment}
`;

export const problemViewFragment = gql`
  fragment ProblemViewFragment on ProblemView {
    awards {
      name
      material {
        ...AwardMaterialFragment
      }
      tackling {
        bestAchievement {
          ...AwardAchievementFragment
          submission {
            id
          }
        }
      }
    }
    tackling {
      ...ProblemTacklingFragment
      submissions { ...SubmissionFragment }
    }
  }

  fragment ProblemTacklingFragment on ProblemTackling {
    totalScore {
      ...ScoreAwardGradeFragment
    }
    canSubmit
  }

  ${submissionFragment}
  ${scoreAwardGradeFragment}
  ${awardMaterialFragment}
  ${awardAchievementFragment}
`;
