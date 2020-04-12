import { gql } from '@apollo/client';
import React from 'react';
import { TitleFieldFragment } from '../../generated/graphql-types';
import { FragmentProps } from '../../util/fragment-props';
import { textFragment } from '../text';

export function TitleField({ data }: FragmentProps<TitleFieldFragment>) {
  return <>{data.title.variant}</>;
}

export const titleFieldFragment = gql`
  fragment TitleField on TitleField {
    title {
      ...Text
    }
  }

  ${textFragment}
`;
