import gql from 'graphql-tag';

import { scoreRangeFragment } from './score';
import { textFragment } from './text';

export const awardFragment = gql`
  fragment AwardFragment on Award {
    name
    title { ...TextFragment }
    content {
      __typename
      ... on ScoreAwardContent {
        range {
          ...ScoreRangeFragment
        }
      }
    }
  }

  ${textFragment}
  ${scoreRangeFragment}
`;

export const awardOutcomeFragment = gql`
  fragment AwardOutcomeFragment on AwardOutcome {
    award {
      ...AwardFragment
    }
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

  ${awardFragment}
`;
