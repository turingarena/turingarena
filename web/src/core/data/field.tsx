import { gql } from '@apollo/client';
import React from 'react';
import { FieldFragment } from '../../generated/graphql-types';
import { unexpected } from '../../util/check';
import { FragmentProps } from '../../util/fragment-props';
import { DateTimeField, dateTimeFieldFragment } from './date-time-field';
import { FulfillmentField, fulfillmentFieldFragment, ScoreField, scoreFieldFragment } from './grade-field';
import { HeaderField, headerFieldFragment } from './header-field';
import { MemoryUsageField, memoryUsageFieldFragment } from './memory-usage-field';
import { MessageField, messageFieldFragment } from './message-field';
import { TimeUsageField, timeUsageFieldFragment } from './time-usage-field';

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
    case 'HeaderField':
      return <HeaderField data={data} />;
    case 'DateTimeField':
      return <DateTimeField data={data} />;
    default:
      return unexpected(data);
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
    ... on HeaderField {
      ...HeaderField
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
    ... on DateTimeField {
      ...DateTimeField
    }
  }

  ${headerFieldFragment}
  ${fulfillmentFieldFragment}
  ${scoreFieldFragment}
  ${memoryUsageFieldFragment}
  ${messageFieldFragment}
  ${timeUsageFieldFragment}
  ${dateTimeFieldFragment}
`;
