import { gql } from '@apollo/client';

export const timeUsageFieldFragment = gql`
  fragment TimeUsage on TimeUsage {
    seconds
  }

  fragment TimeUsageField on TimeUsageField {
    timeUsage {
      ...TimeUsage
    }
    timeUsageMaxRelevant {
      ...TimeUsage
    }
    timeUsagePrimaryWatermark {
      ...TimeUsage
    }
  }
`;
