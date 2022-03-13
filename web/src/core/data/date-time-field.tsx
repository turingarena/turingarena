import { gql } from '@apollo/client';
import { DateTime } from 'luxon';
import React from 'react';
import { DateTimeFieldFragment } from '../../generated/graphql-types';
import { FragmentProps } from '../../util/fragment-props';

export const dateTimeFieldFragment = gql`
  fragment DateTimeField on DateTimeField {
    dateTime {
      local
    }
  }
`;

export function DateTimeField({ data }: FragmentProps<DateTimeFieldFragment>) {
  const { dateTime } = data;
  if (dateTime === null) return null;
  return <>{DateTime.fromISO(dateTime.local).toRelative() ?? `${dateTime.local}`}</>;
}
