import { gql } from 'apollo-server-core';

export const genericGradingSchema = gql`
    interface GenericGradingState {
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
