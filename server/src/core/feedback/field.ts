import { gql } from 'apollo-server-core';

export const fieldSchema = gql`
    union Field = ScoreField | FulfillmentField
`;
