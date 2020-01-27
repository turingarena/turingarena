import { gql } from 'apollo-server-core';

export const messageSchema = gql`
    "Field containing a textual message."
    type MessageValue {
        "The text of this message, if known."
        text: Text
    }
`;
