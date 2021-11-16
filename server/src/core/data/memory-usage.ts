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
        """
        Maximum meaningful value, used to dermine the scale of the numeric representation.
        Null if the value is to be represented exactly (e.g. a memory limit).
        """
        memoryUsageMaxRelevant: MemoryUsage
        "Main upper limit on this memory usage to show users, if any."
        memoryUsageWatermark: MemoryUsage

        valence: Valence
    }

    "Column containing memory usages."
    type MemoryUsageColumn implements TitledColumn {
        title: Text!
    }
`;
