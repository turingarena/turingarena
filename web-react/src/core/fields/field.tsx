import { gql } from '@apollo/client';
import React from 'react';
import { FieldFragment } from '../../generated/graphql-types';
import { FragmentProps } from '../../util/fragment-props';
import { FulfillmentField, fulfillmentFieldFragment, ScoreField, scoreFieldFragment } from './grade-field';
import { indexFieldFragment } from './index-field';
import { MemoryUsageField, memoryUsageFieldFragment } from './memory-usage-field';
import { MessageField, messageFieldFragment } from './message-field';
import { TimeUsageField, timeUsageFieldFragment } from './time-usage-field';
import { TitleField, titleFieldFragment } from './title-field';

export function Field({ data }: FragmentProps<FieldFragment>) {
  switch (data.__typename) {
    case 'TimeUsageField':
      return <TimeUsageField data={data} />;
    case 'MemoryUsageField':
      return <MemoryUsageField data={data} />;
    case 'FulfillmentField':
      return <FulfillmentField data={data} />;
    case 'ScoreField':
      return <ScoreField data={data} />;
    case 'MessageField':
      return <MessageField data={data} />;
    case 'TitleField':
      return <TitleField data={data} />;
    case 'IndexField':
    default:
      return <h1>Not implemented</h1>;
  }
}

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
