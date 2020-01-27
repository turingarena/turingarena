import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../../main/resolver-types';
import { FulfillmentField, FulfillmentGrade, FulfillmentGradeDomain } from './fulfillment';
import { ScoreField, ScoreGrade, ScoreGradeDomain } from './score';

export const gradeSchema = gql`
    """
    Indicates how well something is achieved, with a concept of ordering from a lowest grade to highest grade.
    Currently, grades are either scores (numeric grades) or fulfillments (boolean grades).
    The ordering of grades is useful to define, e.g., the highest grade achieved for an award during a contest.
    """
    union Grade = ScoreGrade | FulfillmentGrade

    "Indicates how a grade is expressed, and its range."
    union GradeDomain = ScoreGradeDomain | FulfillmentGradeDomain

    "Field containing a grade."
    union GradeField = ScoreField | FulfillmentField
`;

export const gradeResolvers: ResolversWithModels<{
    Grade: ScoreGrade | FulfillmentGrade;
    GradeDomain: ScoreGradeDomain | FulfillmentGradeDomain;
    GradeField: ScoreField | FulfillmentField;
}> = {
    Grade: {
        __resolveType: grade => {
            if (grade instanceof ScoreGrade) return 'ScoreGrade';
            if (grade instanceof FulfillmentGrade) return 'FulfillmentGrade';
            throw new Error(`Unknown grade domain ${grade}`);
        },
    },
    GradeDomain: {
        __resolveType: domain => {
            if (domain instanceof ScoreGradeDomain) return 'ScoreGradeDomain';
            if (domain instanceof FulfillmentGradeDomain) return 'FulfillmentGradeDomain';
            throw new Error(`Unknown grade domain ${domain}`);
        },
    },
    GradeField: {
        __resolveType: field => {
            if (field instanceof ScoreField) return 'ScoreField';
            if (field instanceof FulfillmentField) return 'FulfillmentField';
            throw new Error(`Unknown grade variable ${field}`);
        },
    },
};
