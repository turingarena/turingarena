import { gql } from '@apollo/client';
import React from 'react';
import { HeaderFieldFragment } from '../../generated/graphql-types';
import { FragmentProps } from '../../util/fragment-props';
import { Text, textFragment } from '../text';

export function HeaderField({ data }: FragmentProps<HeaderFieldFragment>) {
  return <Text data={data.title} />;
}

export const headerFieldFragment = gql`
  fragment HeaderField on HeaderField {
    title {
      ...Text
    }
  }

  ${textFragment}
`;
