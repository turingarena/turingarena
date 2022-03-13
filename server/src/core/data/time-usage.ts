import { gql } from 'apollo-server-core';
import { ApiOutputValue } from '../../main/graphql-types';
import { Valence } from './valence';
import { Text } from './text';

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
        """
        Maximum meaningful value, used to dermine the scale of the numeric representation.
        Null if the value is to be represented exactly (e.g. a time limit).
        """
        timeUsageMaxRelevant: TimeUsage
        "Main upper limit on this time usage to show users, if any."
        timeUsageWatermark: TimeUsage

        valence: Valence
    }

    "Column containing time usages."
    type TimeUsageColumn implements TitledColumn {
        title: Text!
    }
`;

export class TimeUsage implements ApiOutputValue<'TimeUsage'> {
    __typename = 'TimeUsage' as const;

    constructor(readonly seconds: number) {}
}

export class TimeUsageField implements ApiOutputValue<'TimeUsageField'> {
    __typename = 'TimeUsageField' as const;

    constructor(
        readonly timeUsage: TimeUsage | null,
        readonly timeUsageMaxRelevant: TimeUsage | null,
        readonly timeUsageWatermark: TimeUsage | null,
        readonly valence: Valence | null,
    ) {}
}

export class TimeUsageColumn implements ApiOutputValue<'TimeUsageColumn'> {
    __typename = 'TimeUsageColumn' as const;

    constructor(readonly title: Text) {}
}
