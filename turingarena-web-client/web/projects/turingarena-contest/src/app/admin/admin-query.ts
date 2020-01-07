import gql from 'graphql-tag';

import { awardAchievementFragment } from '../fragments/awards';
import { contestMaterialFragment } from '../fragments/contest';
import { problemMaterialFragment } from '../fragments/material';
import { scoreRangeFragment } from '../fragments/score';

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

  fragment AdminSubmissionFragment on Submission {
    id
    problem {
      name
    }
    userId
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
        ...AdminSubmissionFragment
      }
      scoreRange {
        ...ScoreRangeFragment
      }
    }
  }
  ${contestMaterialFragment}
  ${problemMaterialFragment}
  ${scoreRangeFragment}
`;
