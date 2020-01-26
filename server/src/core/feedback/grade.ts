import { gql } from 'apollo-server-core';

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
