import { gql } from 'apollo-server-core';

export const memoryUsageSchema = gql`
    "Quantity of memory used for some computation."
    type MemoryUsage {
        "Quantity of memory expressed in bytes."
        bytes: Float!
    }

    "Field containing a memory usage, i.e., the quantity of memory used for some computation."
    type MemoryUsageField implements HasValence {
        "The memory usage, if known."
        memoryUsage: MemoryUsage
        "Maximum value over which the precise quantity of memory used is not relevant anymore."
        memoryUsageMaxRelevant: MemoryUsage!
        "Main upper limit on this memory usage to show users, if any."
        memoryUsagePrimaryWatermark: MemoryUsage

        valence: Valence
    }

    "Column containing memory usages."
    type MemoryUsageColumn implements TitledColumn {
        title: Text!
    }
`;
