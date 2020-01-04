import gql from 'graphql-tag';

import { rusageFragment } from './rusage';

export const evaluationFragment = gql`
  fragment TextValueFragment on TextValue {
    text {
      value
    }
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

  fragment SubmissionEvaluationFragment on Submission {
    evaluation {
      events { ...EventFragment }
    }
  }

  ${rusageFragment}
`;
