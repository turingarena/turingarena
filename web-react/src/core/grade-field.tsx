import { gql } from '@apollo/client';
import { fulfillmentFieldFragment } from './fulfillment-field';
import { scoreFieldFragment } from './score-field';

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
