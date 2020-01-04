import gql from 'graphql-tag';

import { awardOutcomeFragment } from '../fragments/awards';
import { contestMaterialFragment } from '../fragments/contest';
import { problemMaterialFragment } from '../fragments/material';
import { scoreRangeFragment } from '../fragments/score';

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
      material {
        ...ContestMaterialFragment
      }
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
  ${contestMaterialFragment}
  ${awardOutcomeFragment}
  ${problemMaterialFragment}
  ${scoreRangeFragment}
`;
