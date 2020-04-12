import { gql } from '@apollo/client';
import React from 'react';
import { TitleFieldFragment } from '../../generated/graphql-types';
import { FragmentProps } from '../../util/fragment-props';
import { Text, textFragment } from '../text';

export function TitleField({ data }: FragmentProps<TitleFieldFragment>) {
  return <Text data={data.title} />;
}

export const titleFieldFragment = gql`
  fragment TitleField on TitleField {
    title {
      ...Text
    }
  }

  ${textFragment}
`;
