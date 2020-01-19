import { gql } from 'apollo-server-core';

export const gradingSchema = gql`
    union Grading = NumericGrading | BooleanGrading
    union Grade = NumericGrade | BooleanGrade
    union GradeDomain = NumericGradeDomain | BooleanGradeDomain
    union GradeValue = NumericGradeValue | BooleanGradeValue
`;
