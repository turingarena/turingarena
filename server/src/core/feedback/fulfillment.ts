import { gql } from 'apollo-server-core';
import { Resolvers } from '../../main/resolver-types';
import { Valence } from './valence';

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
    }
`;

export class FulfillmentGrade {
    constructor(readonly fulfilled: boolean) {}
}

export class FulfillmentGradeDomain {}

export class FulfillmentField {
    constructor(readonly fulfilled: boolean | null) {}
}

export interface FulfillmentModelRecord {
    FulfillmentGrade: FulfillmentGrade;
    FulfillmentGradeDomain: FulfillmentGradeDomain;
    FulfillmentField: FulfillmentField;
}

export const fulfillmentResolvers: Resolvers = {
    FulfillmentGradeDomain: {
        _: () => true,
    },
    FulfillmentField: {
        valence: ({ fulfilled }): Valence | null => (fulfilled === null ? null : fulfilled ? 'SUCCESS' : 'FAILURE'),
    },
};
