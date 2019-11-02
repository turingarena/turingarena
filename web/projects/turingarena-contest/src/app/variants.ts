import gql from 'graphql-tag';

export const variantAttributeFragment = gql`
  fragment VariantAttributeFragment on VariantAttribute {
    key
    value
  }
`;
