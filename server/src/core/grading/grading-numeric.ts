import { gql } from 'apollo-server-core';

export const numericGradingSchema = gql`
    type NumericGrading implements GenericGrading {
        domain: NumericGradeDomain!
        grade: NumericGrade
        valence: Valence
    }

    type NumericGrade implements GenericGrade {
        domain: NumericGradeDomain!
        value: NumericGradeValue!
        valence: Valence!
    }

    type NumericGradeDomain {
        max: Int!
        decimalPrecision: Int!
        allowPartial: Boolean!
    }

    type NumericGradeValue {
        score: Int!
    }
`;
