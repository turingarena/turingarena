import { gql } from '@apollo/client';
import React from 'react';
import { FulfillmentFieldFragment, GradeFieldFragment, ScoreFieldFragment } from '../../generated/graphql-types';
import { unexpected } from '../../util/check';
import { FragmentProps } from '../../util/fragment-props';

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

export function ScoreField({ data }: FragmentProps<ScoreFieldFragment>) {
  // TODO: accept styling from caller

  return (
    <>
      {data.score === null ? (
        <>{data.scoreRange.max.toFixed(data.scoreRange.decimalDigits)}</>
      ) : (
        <>
          <span className="score">{data.score.toFixed(data.scoreRange.decimalDigits)}</span>
          <small className="score-range">
            {' / '}
            {data.scoreRange.max.toFixed(data.scoreRange.decimalDigits)}
          </small>
        </>
      )}
    </>
  );
}

export const FulfillmentField = ({ data }: FragmentProps<FulfillmentFieldFragment>) => {
  const check = <>&#x2713;</>;
  const cross = <>&#x2717;</>;

  switch (data.fulfilled) {
    case null:
    case true:
      return check;
    case false:
      return cross;
    default:
      return unexpected(data.fulfilled);
  }
};

export function GradeField({ data }: { data: GradeFieldFragment }) {
  switch (data.__typename) {
    case 'ScoreField':
      return ScoreField({ data });
    case 'FulfillmentField':
      return FulfillmentField({ data });
    default:
      throw unexpected(data);
  }
}
