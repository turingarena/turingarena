import gql from 'graphql-tag';

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
