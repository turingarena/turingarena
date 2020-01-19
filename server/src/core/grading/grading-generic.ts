import { gql } from 'apollo-server-core';

export const genericGradingSchema = gql`
    interface GenericGrading {
        domain: GradeDomain!
        grade: GenericGrade
        valence: Valence
    }

    interface GenericGrade {
        domain: GradeDomain!
        value: GradeValue!
        valence: Valence!
    }
`;
