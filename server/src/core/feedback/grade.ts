import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../../main/resolver-types';
import { FulfillmentDomain, FulfillmentVariable } from './fulfillment';
import { ScoreDomain, ScoreVariable } from './score';

export const gradeSchema = gql`
    """
    Object containing a grade.

    Grades are values with a concept of ordering from lowest to highest.
    This order is useful to define, e.g., the highest grade achieved for an award during a contest.

    Currently, grades are either scores (numeric grades) or fulfillments (boolean)
    """
    union GradeValue = ScoreValue | FulfillmentValue
    "Domain of a grade. See: GradeValue."
    union GradeDomain = ScoreDomain | FulfillmentDomain
    "Variable containing a grade. See: GradeValue."
    union GradeVariable = ScoreVariable | FulfillmentVariable

    # TODO: consider adding the concept of "ratings", i.e., numerical grades not meant to be added together

    "Object containing a grade. See: GradeValue."
    interface GenericGradeValue {
        valence: Valence!
        domain: GradeDomain!
    }

    "Variable containing a grade. See: GradeValue."
    interface GenericGradeVariable {
        domain: GradeDomain!
        value: GenericGradeValue
    }
`;

export const gradeResolvers: ResolversWithModels<{
    GradeDomain: ScoreDomain | FulfillmentDomain;
    GradeVariable: ScoreVariable | FulfillmentVariable;
}> = {
    GradeDomain: {
        __resolveType: domain => {
            if (domain instanceof ScoreDomain) return 'ScoreDomain';
            if (domain instanceof FulfillmentDomain) return 'FulfillmentDomain';
            throw new Error(`Unknown grade domain ${domain}`);
        },
    },
    GradeVariable: {
        __resolveType: variable => {
            if (variable instanceof ScoreVariable) return 'ScoreVariable';
            if (variable instanceof FulfillmentVariable) return 'FulfillmentVariable';
            throw new Error(`Unknown grade variable ${variable}`);
        },
    },
};
