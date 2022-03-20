import { gql } from 'apollo-server-core';
import { ApiOutputValue } from '../../main/graphql-types';
import { Text } from './text';

export const fulfillmentSchema = gql`
    "A grade expressed as a boolean value: fulfilled or not."
    type FulfillmentGrade {
        "Value of this grade: fulfilled (true) or not fulfilled (false)."
        fulfilled: Boolean!
    }

    "Indicates that a grade is expressed as a fulfillment (boolean)."
    type FulfillmentGradeDomain {
        "Dummy field."
        _: Boolean
    }

    "Field indicating whether something is fulfilled or not."
    type FulfillmentField implements HasValence {
        "Value of this field: fulfilled (true), not fulfilled (false), or unknown (null)."
        fulfilled: Boolean
        "Qualitative feeling (valence) associated with this fulfillment, if any."
        valence: Valence
    }

    "Column containing boolean values indicating whether something is fulfilled or not."
    type FulfillmentColumn implements TitledColumn {
        title: Text!
        fieldIndex: Int!
    }
`;

export class FulfillmentGrade implements ApiOutputValue<'FulfillmentGrade'> {
    constructor(readonly fulfilled: boolean) {}
    __typename = 'FulfillmentGrade' as const;
    valence = this.fulfilled ? 'SUCCESS' : 'FAILURE';
}

export class FulfillmentGradeDomain implements ApiOutputValue<'FulfillmentGradeDomain'> {
    __typename = 'FulfillmentGradeDomain' as const;
    _ = null;
}

export class FulfillmentField implements ApiOutputValue<'FulfillmentField'> {
    constructor(readonly fulfilled: boolean | null) {}
    __typename = 'FulfillmentField' as const;
    valence = this.fulfilled === null ? null : this.fulfilled ? ('SUCCESS' as const) : ('FAILURE' as const);
}

export class FulfillmentColumn implements ApiOutputValue<'FulfillmentColumn'> {
    __typename = 'FulfillmentColumn' as const;

    constructor(readonly title: Text, readonly fieldIndex: number) {}
}
