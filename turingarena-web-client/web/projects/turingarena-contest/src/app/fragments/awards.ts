import gql from 'graphql-tag';

import { scoreRangeFragment } from './score';
import { textFragment } from './text';

export const scoreAwardDomainFragment = gql`
  fragment ScoreAwardDomainFragment on ScoreAwardDomain {
    range {
      ...ScoreRangeFragment
    }
  }

  ${scoreRangeFragment}
`;


export const awardDomainFragment = gql`
  fragment AwardDomainFragment on AwardDomain {
    __typename
    ... on ScoreAwardDomain {
      ...ScoreAwardDomainFragment
    }
  }

  ${scoreAwardDomainFragment}
`;

export const awardMaterialFragment = gql`
  fragment AwardMaterialFragment on AwardMaterial {
    title {
      ...TextFragment
    }
    domain {
      ...AwardDomainFragment
    }
  }

  ${textFragment}
  ${awardDomainFragment}
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

export const scoreAwardValueFragment = gql`
  fragment ScoreAwardValueFragment on ScoreAwardValue {
    score
  }
`;

export const badgeAwardValueFragment = gql`
  fragment BadgeAwardValueFragment on BadgeAwardValue {
    badge
  }
`;

export const awardValueFragment = gql`
  fragment AwardValueFragment on AwardValue {
    ... on BadgeAwardValue {
      ...BadgeAwardValueFragment
    }
    ... on ScoreAwardValue {
      ...ScoreAwardValueFragment
    }
  }

  ${scoreAwardValueFragment}
  ${badgeAwardValueFragment}
`;

export const scoreAwardGradeFragment = gql`
  fragment ScoreAwardGradeFragment on ScoreAwardGrade {
    domain {
      ...ScoreAwardDomainFragment
    }
    value {
      ...ScoreAwardValueFragment
    }
  }

  ${scoreAwardDomainFragment}
  ${scoreAwardValueFragment}
`;

export const awardGradeFragment = gql`
  fragment AwardGradeFragment on AwardGrade {
    __typename
    ... on ScoreAwardGrade {
      ...ScoreAwardGradeFragment
    }
    ... on BadgeAwardGrade {
      domain {
        __typename
      }
      value {
        ...BadgeAwardValueFragment
      }
    }
  }

  ${scoreAwardDomainFragment}
  ${scoreAwardGradeFragment}
  ${badgeAwardValueFragment}
`;

export const awardAchievementFragment = gql`
  fragment AwardAchievementFragment on AwardAchievement {
    award {
      ...AwardFragment
    }
    grade {
      ...AwardGradeFragment
    }
  }

  ${awardFragment}
  ${awardGradeFragment}
`;
