import { gql } from '@apollo/client';
import React from 'react';
import { MessageFieldFragment } from '../../generated/graphql-types';
import { FragmentProps } from '../../util/fragment-props';
import { Text, textFragment } from '../text';

export function MessageField({ data }: FragmentProps<MessageFieldFragment>) {
  return <>{data.message !== null && <Text data={data.message} />}</>;
}

export const messageFieldFragment = gql`
  fragment MessageField on MessageField {
    message {
      ...Text
    }
  }

  ${textFragment}
`;
