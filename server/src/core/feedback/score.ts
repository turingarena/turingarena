import { gql } from 'apollo-server-core';
import { Resolvers } from '../../main/resolver-types';
import { Valence } from './valence';

export const scoreSchema = gql`
    "Defines the possible values for a score."
    type ScoreRange {
        "Maximum number of points, inclusive."
        max: Float!
        "How many decimal digits are included and relevant."
        decimalDigits: Int!
        "Whether partial scores, i.e., between zero and max points, are allowed."
        allowPartial: Boolean!
    }

    "A grade expressed as a number of points from zero to some maximum value."
    type ScoreGrade {
        "The number of points."
        score: Float!
        "Range of possible values for the number of points."
        scoreRange: ScoreRange!
    }

    "Indicates that a grade is expressed as a score, and specifies its range."
    type ScoreGradeDomain {
        "Range of possible values for the number of points."
        scoreRange: ScoreRange!
    }

    "Field containing a score."
    type ScoreField implements HasValence {
        "The number of points, if known."
        score: Float
        "Qualitative feeling (valence) associated with this score, if any."
        valence: Valence
        "Defines the possible values for 'score'."
        scoreRange: ScoreRange!
    }

    "Column containing scores."
    type ScoreColumn implements TitledColumn {
        title: Text!
    }
`;

export class ScoreGrade {
    constructor(readonly scoreRange: ScoreRange, readonly score: number) {}

    static total(values: ScoreGrade[]) {
        return new ScoreGrade(
            ScoreRange.total(values.map(v => v.scoreRange)),
            values.map(v => v.score).reduce((a, b) => a + b, 0),
        );
    }
}

export class ScoreRange {
    constructor(readonly max: number, readonly decimalDigits: number, readonly allowPartial: boolean) {}

    static total(domains: ScoreRange[]) {
        return new ScoreRange(
            domains.map(d => d.max).reduce((a, b) => a + b, 0),
            domains.map(d => d.decimalDigits).reduce((a, b) => Math.max(a, b), 0),
            true,
        );
    }
}

export class ScoreGradeDomain {
    constructor(readonly scoreRange: ScoreRange) {}
}

export class ScoreField {
    constructor(readonly scoreRange: ScoreRange, readonly score: number | null) {}
}

export interface ScoreModelRecord {
    ScoreGrade: ScoreGrade;
    ScoreGradeDomain: ScoreGradeDomain;
    ScoreField: ScoreField;
}

export const scoreResolvers: Resolvers = {
    ScoreField: {
        score: f => f.score,
        scoreRange: f => f.scoreRange,
        valence: ({ scoreRange: { max }, score: value }): Valence | null =>
            value === null ? null : value >= max ? 'SUCCESS' : value > 0 ? 'PARTIAL' : 'FAILURE',
    },
};
