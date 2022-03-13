import { gql } from '@apollo/client';
import { css } from 'emotion';
import React from 'react';
import { HeaderFieldFragment } from '../../generated/graphql-types';
import { FragmentProps } from '../../util/fragment-props';
import { Text, textFragment } from './text';

export function HeaderField({ data }: FragmentProps<HeaderFieldFragment>) {
  return (
    <span
      className={css`
        font-weight: bold;
      `}
    >
      <Text data={data.title} />
    </span>
  );
}

export const headerFieldFragment = gql`
  fragment HeaderField on HeaderField {
    title {
      ...Text
    }
    index
  }

  ${textFragment}
`;
