import { gql } from 'apollo-server-core';

export const timeUsageSchema = gql`
    "Quantity of CPU time used for some computation."
    type TimeUsage {
        "CPU time expressed in bytes"
        bytes: Int!
    }

    "Object containing a time usage, i.e., the quantity of CPU time used for some computation."
    type TimeUsageValue implements GenericVariableValue {
        "The CPU time used."
        timeUsage: TimeUsage!
        "Describes the possible values for 'timeUsage'."
        domain: TimeUsageDomain!
    }

    "Describes the possible values for a time usage."
    type TimeUsageDomain {
        "Maximum value over which the precise quantity of CPU time used is not relevant anymore."
        maxRelevant: TimeUsage!
        "Main upper limit on this time usage to show users, if any."
        primaryWatermark: TimeUsage
    }

    "Variable containing a time usage."
    type TimeUsageVariable implements GenericVariable {
        domain: TimeUsageDomain!
        value: TimeUsageValue
    }
`;
