import { gql } from 'apollo-server-core';
import { Valence } from '../../generated/graphql-types';
import { ResolversWithModels } from '../../main/resolver-types';

export const scoreSchema = gql`
    "Object containing a score, i.e., a (possibly decimal) number of points from zero to some maximum value."
    type ScoreValue implements GenericGradeValue {
        "The number of points."
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

export class ScoreDomain {
    constructor(readonly max: number, readonly decimalDigits: number, readonly allowPartial: boolean) {}

    zero() {
        return new ScoreValue(this, 0);
    }

    variable(value: ScoreValue | null) {
        return new ScoreVariable(this, value);
    }

    static total(domains: ScoreDomain[]) {
        return new ScoreDomain(
            domains.map(d => d.max).reduce((a, b) => a + b),
            domains.map(d => d.decimalDigits).reduce((a, b) => Math.max(a, b)),
            true,
        );
    }
}

export class ScoreValue {
    constructor(readonly domain: ScoreDomain, readonly score: number) {}

    static total(values: ScoreValue[]) {
        return new ScoreValue(
            ScoreDomain.total(values.map(v => v.domain)),
            values.map(v => v.score).reduce((a, b) => a + b),
        );
    }
}

export class ScoreVariable {
    constructor(readonly domain: ScoreDomain, readonly value: ScoreValue | null) {}
}

export const scoreResolvers: ResolversWithModels<{
    ScoreValue: ScoreValue;
}> = {
    ScoreValue: {
        valence: ({ domain: { max }, score }): Valence =>
            score >= max ? 'SUCCESS' : score > 0 ? 'PARTIAL' : 'FAILURE',
    },
};
