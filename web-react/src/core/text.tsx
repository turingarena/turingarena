import { gql } from '@apollo/client';

export const textFragment = gql`
  fragment Text on Text {
    variant
  }
`;
