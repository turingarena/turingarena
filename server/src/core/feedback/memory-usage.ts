import { gql } from 'apollo-server-core';

export const memoryUsageSchema = gql`
    "Quantity of memory used for some computation."
    type MemoryUsage {
        "Quantity of memory expressed in bytes"
        bytes: Int!
    }

    "Object containing a memory usage, i.e., the quantity of memory used for some computation."
    type MemoryUsageValue implements GenericVariableValue {
        "The memory usage."
        memoryUsage: MemoryUsage!
        "Describes the possible values for 'memoryUsage'."
        domain: MemoryUsageDomain!
    }

    "Describes the possible values for a memory usage."
    type MemoryUsageDomain {
        "Maximum value over which the precise quantity of memory used is not relevant anymore."
        maxRelevant: MemoryUsage!
        "Main upper limit on this memory usage to show users, if any."
        primaryWatermark: MemoryUsage
    }

    "Variable containing a memory usage."
    type MemoryUsageVariable implements GenericVariable {
        domain: MemoryUsageDomain!
        value: MemoryUsageValue
    }
`;
