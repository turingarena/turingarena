import { gql } from 'apollo-server-core';

export const booleanGradingSchema = gql`
    type BooleanGrading implements GenericGrading {
        domain: BooleanGradeDomain!
        grade: BooleanGrade
        valence: Valence
    }

    type BooleanGrade implements GenericGrade {
        domain: BooleanGradeDomain!
        value: BooleanGradeValue!
        valence: Valence!
    }

    type BooleanGradeDomain {
        _: Boolean
    }

    type BooleanGradeValue {
        achieved: Boolean!
    }
`;
