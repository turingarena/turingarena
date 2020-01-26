import { gql } from 'apollo-server-core';

export const scoreSchema = gql`
    "Object containing a score, i.e., a number of points from zero to some maximum value."
    type ScoreValue implements GenericGradeValue {
        "Number of points."
        score: Float!
        "Qualitative feeling (valence) associated with this score."
        valence: Valence!
        "Defines the possible values for 'score'."
        domain: ScoreDomain!
    }

    "Defines the possible numbers of points for a score"
    type ScoreDomain {
        "Maximum number of points, inclusive."
        max: Float!
        "How many decimal digits are included and relevant."
        decimalDigits: Int!
        "Whether partial scores, i.e., between zero and max points, are allowed."
        allowPartial: Boolean!
    }

    "Variable containing a score."
    type ScoreVariable implements GenericGradeVariable {
        domain: ScoreDomain!
        value: ScoreValue
    }
`;
