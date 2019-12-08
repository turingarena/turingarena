import gql from 'graphql-tag';

export const submissionAwardFragment = gql`
  fragment SubmissionAwardFragment on SubmissionAward {
    awardName
    value {
      ... on BadgeAwardValue {
        badge
      }
      ... on ScoreAwardValue {
        score
      }
    }
  }
`;
