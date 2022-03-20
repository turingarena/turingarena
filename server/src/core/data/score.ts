import { gql } from 'apollo-server-core';
import { ApiOutputValue } from '../../main/graphql-types';
import { Text } from './text';
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
        fieldIndex: Int!
    }
`;

export class ScoreGrade implements ApiOutputValue<'ScoreGrade'> {
    constructor(readonly scoreRange: ScoreRange, readonly score: number) {}

    __typename = 'ScoreGrade' as const;

    static total(values: ScoreGrade[]) {
        return new ScoreGrade(
            ScoreRange.total(values.map(v => v.scoreRange)),
            values.map(v => v.score).reduce((a, b) => a + b, 0),
        );
    }
}

export class ScoreRange implements ApiOutputValue<'ScoreRange'> {
    constructor(readonly max: number, readonly decimalDigits: number, readonly allowPartial: boolean) {}
    __typename = 'ScoreRange' as const;

    static total(domains: ScoreRange[]) {
        return new ScoreRange(
            domains.map(d => d.max).reduce((a, b) => a + b, 0),
            domains.map(d => d.decimalDigits).reduce((a, b) => Math.max(a, b), 0),
            true,
        );
    }
}

export class ScoreGradeDomain implements ApiOutputValue<'ScoreGradeDomain'> {
    constructor(readonly scoreRange: ScoreRange) {}
    __typename = 'ScoreGradeDomain' as const;
}

export class ScoreField implements ApiOutputValue<'ScoreField'> {
    constructor(readonly scoreRange: ScoreRange, readonly score: number | null) {}
    __typename = 'ScoreField' as const;

    valence(): Valence | null {
        return this.score === null
            ? null
            : this.score >= this.scoreRange.max
            ? 'SUCCESS'
            : this.score > 0
            ? 'PARTIAL'
            : 'FAILURE';
    }
}

export class ScoreColumn implements ApiOutputValue<'ScoreColumn'> {
    __typename = 'ScoreColumn' as const;

    constructor(readonly title: Text, readonly fieldIndex: number) {}
}
