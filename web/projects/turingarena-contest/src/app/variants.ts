import gql from 'graphql-tag';

export const fileFragment = gql`
  fragment VariantAttributeFragment on VariantAttribute {
    key
    value
  }
`;
