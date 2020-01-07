import gql from 'graphql-tag';

import { awardGradingFragment, scoreAwardGradingFragment } from './awards';
import { rusageFragment } from './rusage';
import { textFragment } from './text';

export const evaluationEventFragment = gql`
  fragment TextValueFragment on TextValue {
    text { ...TextFragment }
  }

  fragment ScoreValueFragment on ScoreValue {
    score
  }

  fragment TimeUsageValueFragment on TimeUsageValue {
    timeUsage { ...TimeUsageFragment }
  }

  fragment MemoryUsageValueFragment on MemoryUsageValue {
    memoryUsage { ...MemoryUsageFragment }
  }

  fragment ValenceValueFragment on ValenceValue {
    valence
  }

  fragment ValueFragment on Value {
    __typename
    ... on TextValue { ...TextValueFragment }
    ... on ScoreValue { ...ScoreValueFragment }
    ... on TimeUsageValue { ...TimeUsageValueFragment }
    ... on MemoryUsageValue { ...MemoryUsageValueFragment }
    ... on ValenceValue { ...ValenceValueFragment }
  }

  fragment EventFragment on Event {
    __typename
    ... on ValueEvent {
      key
      value { ...ValueFragment }
    }
  }

  ${rusageFragment}
  ${textFragment}
`;

export const evaluationFragment = gql`
  fragment EvaluationFragment on Evaluation {
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

  ${scoreAwardGradingFragment}
  ${awardGradingFragment}
`;
