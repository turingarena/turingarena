import gql from 'graphql-tag';
import { variantAttributeFragment } from './variants';

export const fileFragment = gql`
  fragment FileFragment on FileVariant {
    attributes {
      ...VariantAttributeFragment
    }
    name
    type
    content {
      base64
      text
    }
  }
  ${variantAttributeFragment}
`;
