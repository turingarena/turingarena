import { gql } from '@apollo/client';
import { textFragment } from './text';

export const messageFieldFragment = gql`
  fragment MessageField on MessageField {
    message {
      ...Text
    }
  }

  ${textFragment}
`;
