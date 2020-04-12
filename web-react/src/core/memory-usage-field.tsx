import { gql } from '@apollo/client';

export const memoryUsageFieldFragment = gql`
  fragment MemoryUsage on MemoryUsage {
    bytes
  }

  fragment MemoryUsageField on MemoryUsageField {
    memoryUsage {
      ...MemoryUsage
    }
    memoryUsageMaxRelevant {
      ...MemoryUsage
    }
    memoryUsagePrimaryWatermark {
      ...MemoryUsage
    }
  }
`;
