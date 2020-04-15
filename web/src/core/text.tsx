import { gql } from '@apollo/client';
import React from 'react';
import { TextFragment } from '../generated/graphql-types';
import { FragmentProps } from '../util/fragment-props';

export function Text({ data }: FragmentProps<TextFragment>) {
  return <>{data.variant}</>;
}

export const textFragment = gql`
  fragment Text on Text {
    variant
  }
`;
