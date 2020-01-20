import gql from 'graphql-tag';

export const rusageFragment = gql`
  fragment TimeUsageFragment on TimeUsage {
    seconds
  }

  fragment MemoryUsageFragment on MemoryUsage {
    bytes
  }
`;
