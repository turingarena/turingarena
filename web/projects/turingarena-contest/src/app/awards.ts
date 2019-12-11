import gql from 'graphql-tag';

export const awardOutcomeFragment = gql`
  fragment AwardOutcomeFragment on AwardOutcome {
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
