import { gql } from 'apollo-server-core';

export const gradeSchema = gql`
    interface Grading {
        domain: GradeDomain!
        grade: GenericGrade
    }

    type NumericGrading implements Grading {
        domain: NumericGradeDomain!
        grade: NumericGrade
    }

    type BooleanGrading implements Grading {
        domain: BooleanGradeDomain!
        grade: BooleanGrade
    }

    interface GenericGrade {
        domain: GradeDomain!
        value: GradeValue!
        valence: Valence
    }

    type NumericGrade implements GenericGrade {
        domain: NumericGradeDomain!
        value: NumericGradeValue!
        valence: Valence
    }

    type BooleanGrade implements GenericGrade {
        domain: BooleanGradeDomain!
        value: BooleanGradeValue!
        valence: Valence
    }

    union Grade = NumericGrade | BooleanGrade

    type NumericGradeDomain {
        max: Int!
        decimalPrecision: Int!
        allowPartial: Boolean!
    }

    type BooleanGradeDomain {
        _: Boolean
    }

    union GradeDomain = NumericGradeDomain | BooleanGradeDomain

    type NumericGradeValue {
        score: Int!
    }

    type BooleanGradeValue {
        achieved: Boolean!
    }

    union GradeValue = NumericGradeValue | BooleanGradeValue

    enum Valence {
        SUCCESS
        FAILURE
        PARTIAL
        NOMINAL
        SKIPPED
        IGNORED
        BLOCKED
    }
`;
