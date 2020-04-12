import { gql } from '@apollo/client';

export const mediaInlineFragment = gql`
  fragment MediaInline on Media {
    variant {
      name
      type
      url
    }
  }
`;
