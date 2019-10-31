import gql from 'graphql-tag';

export const textFragment = gql`
  fragment TextFragment on TextVariant {
    attributes {
      key
      value
    }
    value
  }
`;
