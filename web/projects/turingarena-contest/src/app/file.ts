import gql from 'graphql-tag';

export const fileFragment = gql`
  fragment FileFragment on FileVariant {
    attributes {
      key
      value
    }
    name
    type
    content {
      base64
    }
  }
`;
