import { gql } from '@apollo/client';
import { fieldFragment } from './fields/field';
import { textFragment } from './text';

export const columnFragment = gql`
  fragment Column on Column {
    ... on TitledColumn {
      title {
        ...Text
      }
    }
  }

  ${textFragment}
`;

export const recordFragment = gql`
  fragment Record on Record {
    fields {
      ...Field
      ... on HasValence {
        valence
      }
    }
  }

  ${fieldFragment}
`;
