import gql from 'graphql-tag';
import { variantAttributeFragment } from './variants';

export const textFragment = gql`
  fragment TextFragment on TextVariant {
    attributes {
      ...VariantAttributeFragment
    }
    value
  }
  ${variantAttributeFragment}
`;
