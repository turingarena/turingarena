import gql from 'graphql-tag';

import { scoreRangeFragment } from './score';
import { textFragment } from './text';

export const awardMaterialFragment = gql`
  fragment AwardMaterialFragment on AwardMaterial {
    title {
      ...TextFragment
    }
    domain {
      __typename
      ... on ScoreAwardDomain {
        range {
          ...ScoreRangeFragment
        }
      }
    }
  }

  ${textFragment}
  ${scoreRangeFragment}
`;

export const awardFragment = gql`
  fragment AwardFragment on Award {
    name
    material {
      ...AwardMaterialFragment
    }
  }

  ${awardMaterialFragment}
`;

export const awardOutcomeFragment = gql`
  fragment AwardOutcomeFragment on AwardOutcome {
    name
    material {
      ...AwardMaterialFragment
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

  ${awardMaterialFragment}
`;
