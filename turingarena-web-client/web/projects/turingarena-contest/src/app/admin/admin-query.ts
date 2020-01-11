import gql from 'graphql-tag';

import { awardAchievementFragment } from '../fragments/awards';
import { contestMaterialFragment } from '../fragments/contest';
import { problemMaterialFragment } from '../fragments/material';
import { scoreRangeFragment } from '../fragments/score';
import { submissionFragment } from '../fragments/submission';

export const adminQuery = gql`
  fragment AdminProblemFragment on Problem {
    name
    material {
      ...MaterialFragment
    }
    scoreRange {
      ...ScoreRangeFragment
    }
  }

  fragment AdminUserFragment on User {
    id
    displayName
  }

  query AdminQuery {
    serverTime
    contest {
      material {
        ...ContestMaterialFragment
      }
      problems {
        ...AdminProblemFragment
      }
      users {
        ...AdminUserFragment
      }
      submissions {
        problem {
          name
        }
        user {
          id
          displayName
        }
        ...SubmissionFragment
      }
      scoreRange {
        ...ScoreRangeFragment
      }
    }
  }
  ${contestMaterialFragment}
  ${problemMaterialFragment}
  ${scoreRangeFragment}
  ${submissionFragment}
`;
