import gql from 'graphql-tag';

export const awardOutcomeFragment = gql`
  fragment AwardOutcomeFragment on AwardOutcome {
    awardName
    value {
      ... AwardValueFragment
    }
  }

  fragment AwardValueFragment on AwardValue {
    ... on BadgeAwardValue {
      ... BadgeAwardValueFragment
    }
    ... on ScoreAwardValue {
      ... ScoreAwardValueFragment
    }
  }

  fragment BadgeAwardValueFragment on BadgeAwardValue {
    badge
  }

  fragment ScoreAwardValueFragment on ScoreAwardValue {
    score
  }
`;
