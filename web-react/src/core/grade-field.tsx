import React from 'react';
import styled from 'styled-components';
import { gql } from '@apollo/client';
import { GradeFieldFragment, ScoreFieldFragment, FulfillmentFieldFragment } from '../generated/graphql-types';

const fulfillmentFieldFragment = gql`
  fragment FulfillmentField on FulfillmentField {
    fulfilled
    valence
  }
`;

const scoreFieldFragment = gql`
  fragment ScoreField on ScoreField {
    scoreRange {
      max
      allowPartial
      decimalDigits
    }
    score
    valence
  }
`;

export const gradeFieldFragment = gql`
  fragment GradeField on GradeField {
    __typename
    ... on FulfillmentField {
      ...FulfillmentField
    }
    ... on ScoreField {
      ...ScoreField
    }
  }

  ${scoreFieldFragment}
  ${fulfillmentFieldFragment}
`;

const ScoreValue = styled.span`
  font-size: 4rem;
`;

const MaxScoreValue = styled.span`
`;

const ScoreField = (data: ScoreFieldFragment) => {
  return (
    <span>
      {data.score === null ? (
        <MaxScoreValue>
          {'+ '}
          {data.scoreRange.max.toFixed(data.scoreRange.decimalDigits)}
        </MaxScoreValue>
      ) : (
        <>
          <ScoreValue>
            {data.score.toFixed(data.scoreRange.decimalDigits)}
          </ScoreValue>
          <MaxScoreValue>
            {' / '}
            {data.scoreRange.max.toFixed(data.scoreRange.decimalDigits)}
          </MaxScoreValue>
        </>
      )}
    </span>
  );
}

const FulfillmentField = (data: FulfillmentFieldFragment) => {
  switch (data.fulfilled) {
    case null:
      return '+';
    case true:
      return '&#x2713';
    case false:
      return '&#x2717;';
  }
};

export function GradeField({data}: {data: GradeFieldFragment}) {
  switch (data.__typename) {
    case 'ScoreField':
      return ScoreField(data);
    case 'FulfillmentField':
      return FulfillmentField(data);
  }
}
