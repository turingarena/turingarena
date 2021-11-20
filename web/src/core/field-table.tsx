import { gql } from '@apollo/client';
import { Valence } from '../generated/graphql-types';
import { fieldFragment } from './data/field';
import { textFragment } from './data/text';

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
    valence
  }

  ${fieldFragment}
`;

export function getTableClassByValence(valence: Valence | null) {
  switch (valence) {
    case 'WARNING':
    case 'PARTIAL':
      return 'table-warning';
    case 'SUCCESS':
      return 'table-success';
    case 'FAILURE':
      return 'table-danger';
    default:
      return '';
  }
}
