import { gql } from 'apollo-server-core';

export const messageSchema = gql`
    "Something that can be assigned a textual message."
    type MessageVariable implements GenericVariable {
        "Dummy object representing the domain of this variable."
        domain: MessageDomain!
        "The score currently assigned to this item, if any. May vary over time."
        value: MessageValue
    }

    "Object containing a textual message."
    type MessageValue implements GenericVariableValue {
        "The text of this message."
        text: Text!
        "Dummy object representing the domain of this value."
        domain: MessageDomain!
    }

    "Dummy type representing the possible values for a message"
    type MessageDomain {
        _: Boolean
    }
`;
