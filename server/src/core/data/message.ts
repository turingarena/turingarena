import { gql } from 'apollo-server-core';

export const messageFieldSchema = gql`
    "Field containing a textual message."
    type MessageField implements HasValence {
        "The text of this message, if known."
        message: Text
        valence: Valence
    }

    "Column containing textual messages."
    type MessageColumn implements TitledColumn {
        title: Text!
    }
`;
