import { gql } from 'apollo-server-core';
import { ApiOutputValue } from '../../main/graphql-types';
import { Text } from './text';
import { Valence } from './valence';

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

export class MessageField implements ApiOutputValue<'MessageField'> {
    __typename = 'MessageField' as const;

    constructor(readonly message: Text | null, readonly valence: Valence | null) {}
}

export class MessageColumn implements ApiOutputValue<'MessageColumn'> {
    __typename = 'MessageColumn' as const;

    constructor(readonly title: Text) {}
}
