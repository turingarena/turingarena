import { gql } from 'apollo-server-core';

export const gradingSchema = gql`
    union GradingState = NumericGradingState | BooleanGradingState
    union Grade = NumericGrade | BooleanGrade
    union GradeDomain = NumericGradeDomain | BooleanGradeDomain
    union GradeValue = NumericGradeValue | BooleanGradeValue
`;
