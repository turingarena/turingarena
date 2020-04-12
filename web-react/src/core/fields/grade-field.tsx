import { gql } from '@apollo/client';
import React from 'react';
import styled from 'styled-components';
import { FulfillmentFieldFragment, GradeFieldFragment, ScoreFieldFragment } from '../../generated/graphql-types';
import { unexpected } from '../util/check';

export const fulfillmentFieldFragment = gql`
  fragment FulfillmentField on FulfillmentField {
    fulfilled
    valence
  }
`;

export const scoreFieldFragment = gql`
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

const MaxScoreValue = styled.span``;

const ScoreField = (data: ScoreFieldFragment) => (
  <span>
    {data.score === null ? (
      <MaxScoreValue>
        {'+ '}
        {data.scoreRange.max.toFixed(data.scoreRange.decimalDigits)}
      </MaxScoreValue>
    ) : (
      <>
        <ScoreValue>{data.score.toFixed(data.scoreRange.decimalDigits)}</ScoreValue>
        <MaxScoreValue>
          {' / '}
          {data.scoreRange.max.toFixed(data.scoreRange.decimalDigits)}
        </MaxScoreValue>
      </>
    )}
  </span>
);

const FulfillmentField = (data: FulfillmentFieldFragment) => {
  switch (data.fulfilled) {
    case null:
      return '+';
    case true:
      return '&#x2713';
    case false:
      return '&#x2717;';
    default:
      return unexpected(data.fulfilled);
  }
};

export function GradeField({ data }: { data: GradeFieldFragment }) {
  switch (data.__typename) {
    case 'ScoreField':
      return ScoreField(data);
    case 'FulfillmentField':
      return FulfillmentField(data);
    default:
      // return unexpected(data.__typename);
      throw Error(''); // FIXME: why doesn't the previous line suffice?
  }
}
