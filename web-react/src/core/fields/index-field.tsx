import { gql } from '@apollo/client';
import React from 'react';
import { IndexFieldFragment } from '../../generated/graphql-types';
import { FragmentProps } from '../../util/fragment-props';

export function IndexField({ data }: FragmentProps<IndexFieldFragment>) {
  return <>{data.index}</>;
}

export const indexFieldFragment = gql`
  fragment IndexField on IndexField {
    index
  }
`;
