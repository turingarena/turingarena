import gql from 'graphql-tag';
import { awardGradingFragment, scoreAwardGradingFragment } from './awards';

export const submissionFragment = gql`
  fragment SubmissionFragment on Submission {
    id
    createdAt
    files {
      fieldId
      typeId
      name
    }
    evaluation {
      status
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

  ${scoreAwardGradingFragment}
  ${awardGradingFragment}
`;
