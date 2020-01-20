import gql from 'graphql-tag';
import {
  awardAchievementFragment,
  awardGradingFragment,
  awardMaterialFragment,
  scoreAwardGradingFragment,
} from './awards';
import { problemMaterialFragment } from './material';
import { scoreRangeFragment } from './score';
import { submissionFragment } from './submission';

export const problemViewFragment = gql`
  fragment ProblemViewFragment on ProblemView {
    awards {
      name
      material {
        ...AwardMaterialFragment
      }
      grading {
        ...AwardGradingFragment
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
    grading {
      ...ScoreAwardGradingFragment
    }
    tackling {
      canSubmit
      submissions {
        ...SubmissionFragment
      }
    }
  }

  ${submissionFragment}
  ${scoreAwardGradingFragment}
  ${awardGradingFragment}
  ${awardMaterialFragment}
  ${awardAchievementFragment}
`;

export const problemFragment = gql`
  fragment ProblemFragment on Problem {
    name
    material {
      ...MaterialFragment
    }
    view(userId: $userId) {
      ...ProblemViewFragment
    }
  }

  ${problemMaterialFragment}
  ${problemViewFragment}
  ${scoreRangeFragment}
`;
