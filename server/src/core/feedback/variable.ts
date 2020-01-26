import { gql } from 'apollo-server-core';

export const variableSchema = gql`
    "A value assigned during evaluation."
    union VariableValue =
          ScoreValue
        | FulfillmentValue
        | ValenceValue
        | MessageValue
        | TimeUsageValue
        | MemoryUsageValue

    "Describes a set of possible values that can be assigned during evaluation."
    union VariableDomain =
          ScoreDomain
        | FulfillmentDomain
        | ValenceDomain
        | MessageDomain
        | TimeUsageDomain
        | MemoryUsageDomain

    "Something that can be assigned a value during evaluation."
    union Variable =
          ScoreVariable
        | FulfillmentVariable
        | ValenceVariable
        | MessageVariable
        | TimeUsageVariable
        | MemoryUsageVariable

    "A value assigned during evaluation."
    interface GenericVariableValue {
        "Describes the possible values."
        domain: VariableDomain!
    }

    "Something that can be assigned a value during evaluation."
    interface GenericVariable {
        domain: VariableDomain!
        value: VariableValue
    }
`;
