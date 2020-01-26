import { gql } from 'apollo-server-core';
import { Valence } from '../../generated/graphql-types';
import { ResolversWithModels } from '../../main/resolver-types';

export const fulfillmentSchema = gql`
    "Object containing whether something is fulfilled or not."
    type FulfillmentValue implements GenericGradeValue {
        "Whether this object represent something fulfilled (true) or not (false)."
        fulfilled: Boolean!
        "Qualitative feeling (valence) associated with this score."
        valence: Valence!
        "Dummy object representing the domain of this value."
        domain: FulfillmentDomain!
    }

    "Dummy type representing the possible values for a fulfillment (always true and false)"
    type FulfillmentDomain {
        _: Boolean
    }

    "Variable containing a fulfillment value."
    type FulfillmentVariable implements GenericGradeVariable {
        domain: FulfillmentDomain!
        value: FulfillmentValue
    }
`;

export class FulfillmentDomain {
    createVariable(fulfilled: boolean | null) {
        return new FulfillmentVariable(fulfilled);
    }
}

export class FulfillmentVariable {
    constructor(readonly value: boolean | null) {}
}

export const fulfillmentResolvers: ResolversWithModels<{
    FulfillmentValue: boolean;
    FulfillmentDomain: FulfillmentDomain;
    FulfillmentVariable: FulfillmentVariable;
}> = {
    FulfillmentValue: {
        fulfilled: fulfilled => fulfilled,
        valence: (fulfilled): Valence => (fulfilled ? 'SUCCESS' : 'FAILURE'),
        domain: () => ({}),
    },
    FulfillmentDomain: {
        _: () => true,
    },
    FulfillmentVariable: {
        domain: () => ({}),
    },
};
