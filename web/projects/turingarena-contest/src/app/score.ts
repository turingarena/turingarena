import gql from 'graphql-tag';

export const scoreRangeFragment = gql`
  fragment ScoreRangeFragment on ScoreRange {
    precision
    max
  }
`;
