import gql from 'graphql-tag';
import { awardAchievementFragment, awardGradingFragment, scoreAwardGradingFragment } from '../fragments/awards';
import { contestMaterialFragment } from '../fragments/contest';
import { evaluationFragment } from '../fragments/evaluation';
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
    problemSetView {
      grading {
        ...ScoreAwardGradingFragment
      }
      problemViews {
        grading {
          ...ScoreAwardGradingFragment
        }
        awards {
          grading {
            ...AwardGradingFragment
          }
        }
      }
    }
  }

  fragment AdminEvaluationFragment on Evaluation {
    ...EvaluationFragment
    submission {
      ...SubmissionFragment
    }
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
      evaluations {
        ...AdminEvaluationFragment
        submission {
          problem {
            name
          }
        }
      }
      scoreRange {
        ...ScoreRangeFragment
      }
      messages {
        id
        createdAt
        kind
        user {
          ...AdminUserFragment
        }
        text
      }
    }
  }
  ${contestMaterialFragment}
  ${problemMaterialFragment}
  ${scoreRangeFragment}
  ${submissionFragment}
  ${scoreAwardGradingFragment}
  ${awardGradingFragment}
  ${evaluationFragment}
`;
