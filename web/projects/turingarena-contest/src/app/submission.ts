import gql from 'graphql-tag';

export const submissionFragment = gql`
  fragment SubmissionFragment on Submission {
    id
    createdAt
    files {
      fieldId
      typeId
      name
      contentBase64
    }
    status
    scores {
      awardName
      score
    }
    badges {
      awardName
      badge
    }
  }
`;
