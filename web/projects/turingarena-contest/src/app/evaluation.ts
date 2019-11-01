import gql from 'graphql-tag';

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
    timeUsage
  }

  fragment MemoryUsageValueFragment on MemoryUsageValue {
    memoryUsage
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

  fragment ValueEventFragment on ValueEvent {
    __typename
    ... on ValueEvent {
      key
      value { ...ValueFragment }
    }
  }

  fragment EvaluationEventFragment on EvaluationEvent {
    event { ...ValueEventFragment }
  }

  fragment SubmissionEvaluationFragment on Submission {
    evaluationEvents { ...EvaluationEventFragment }
  }
`;
