import gql from 'graphql-tag';

import { awardOutcomeFragment } from '../fragments/awards';
import { problemMaterialFragment } from '../fragments/material';
import { scoreRangeFragment } from '../fragments/score';
import { textFragment } from '../fragments/text';

export const adminQuery = gql`
  fragment AdminProblemFragment on Problem {
    name
    material {
      ...MaterialFragment
    }
    totalScoreRange {
      ...ScoreRangeFragment
    }
  }

  fragment AdminUserFragment on User {
    id
    displayName
    contestView {
      totalScore
      totalScoreRange {
        ...ScoreRangeFragment
      }
      problems {
        name
        tackling {
          totalScore
          awards {
            ...AwardOutcomeFragment
          }
        }
      }
    }
  }

  fragment AdminSubmissionFragment on Submission {
    id
    problemName
    userId
  }

  query AdminQuery {
    serverTime
    contestView {
      title { ...TextFragment }
      startTime
      endTime
      totalScoreRange {
        ...ScoreRangeFragment
      }
    }
    problems {
      ...AdminProblemFragment
    }
    users {
      ...AdminUserFragment
    }
    submissions {
      ...AdminSubmissionFragment
    }
  }
  ${awardOutcomeFragment}
  ${problemMaterialFragment}
  ${scoreRangeFragment}
  ${textFragment}
`;
