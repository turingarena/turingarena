import { gql } from 'apollo-server-core';

export const gradeSchema = gql`
    """
    Indicates how well something is achieved, with a concept of ordering from a lowest grade to highest grade.
    Currently, grades are either scores (numeric grades) or fulfillments (boolean grades).
    The ordering of grades is useful to define, e.g., the highest grade achieved for an objective during a contest.
    """
    union Grade = ScoreGrade | FulfillmentGrade

    "Indicates how a grade is expressed, and its range."
    union GradeDomain = ScoreGradeDomain | FulfillmentGradeDomain

    "Field containing a grade."
    union GradeField = ScoreField | FulfillmentField
`;
