import { gql } from 'apollo-server-core';

export const fieldSchema = gql`
    "Container for values to show users af feedback."
    union Field = ScoreField | FulfillmentField | MessageField | TimeUsageField | MemoryUsageField
`;
