import gql from 'graphql-tag';

import { awardOutcomeFragment } from './awards';

export const submissionFragment = gql`
  fragment SubmissionFragment on Submission {
    id
    createdAt
    files {
      fieldId
      typeId
      name
      content {
        base64
      }
    }
    evaluation {
      status
      awards {
        ...AwardOutcomeFragment
      }
      totalScore
    }
  }
  ${awardOutcomeFragment}
`;
