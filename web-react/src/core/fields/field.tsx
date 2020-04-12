import { gql } from '@apollo/client';
import { fulfillmentFieldFragment, scoreFieldFragment } from './grade-field';
import { indexFieldFragment } from './index-field';
import { memoryUsageFieldFragment } from './memory-usage-field';
import { messageFieldFragment } from './message-field';
import { timeUsageFieldFragment } from './time-usage-field';
import { titleFieldFragment } from './title-field';

export const fieldFragment = gql`
  fragment Field on Field {
    ... on FulfillmentField {
      ...FulfillmentField
    }
    ... on ScoreField {
      ...ScoreField
    }
    ... on IndexField {
      ...IndexField
    }
    ... on TitleField {
      ...TitleField
    }
    ... on MessageField {
      ...MessageField
    }
    ... on TimeUsageField {
      ...TimeUsageField
    }
    ... on MemoryUsageField {
      ...MemoryUsageField
    }
  }

  ${fulfillmentFieldFragment}
  ${scoreFieldFragment}
  ${indexFieldFragment}
  ${memoryUsageFieldFragment}
  ${messageFieldFragment}
  ${timeUsageFieldFragment}
  ${titleFieldFragment}
`;
