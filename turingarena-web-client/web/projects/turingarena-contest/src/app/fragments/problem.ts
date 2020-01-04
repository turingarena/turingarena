import gql from 'graphql-tag';

import { awardOutcomeFragment } from './awards';
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
    tackling {
      ...ProblemTacklingFragment
      submissions { ...SubmissionFragment }
    }
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

  ${submissionFragment}
  ${awardOutcomeFragment}
`;
