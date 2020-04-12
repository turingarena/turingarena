import { gql } from '@apollo/client';
import { textFragment } from './text';

export const titleFieldFragment = gql`
  fragment TitleField on TitleField {
    title {
      ...Text
    }
  }

  ${textFragment}
`;
