import { gql } from 'apollo-server-core';

export const timeUsageSchema = gql`
    "Quantity of CPU time used for some computation."
    type TimeUsage {
        "CPU time expressed in seconds"
        seconds: Float!
    }

    "Field containing a time usage, i.e., the quantity of CPU time used for some computation."
    type TimeUsageField implements HasValence {
        "The CPU time used, if known."
        timeUsage: TimeUsage
        "Maximum value over which the precise quantity of CPU time used is not relevant anymore."
        timeUsageMaxRelevant: TimeUsage!
        "Main upper limit on this time usage to show users, if any."
        timeUsageWatermark: TimeUsage

        valence: Valence
    }

    "Column containing time usages."
    type TimeUsageColumn implements TitledColumn {
        title: Text!
    }
`;
