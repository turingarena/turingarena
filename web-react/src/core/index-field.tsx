import { gql } from '@apollo/client';

export const indexFieldFragment = gql`
  fragment IndexField on IndexField {
    index
  }
`;
