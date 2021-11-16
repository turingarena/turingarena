import { gql } from 'apollo-server-core';
import { ApiOutputValue } from '../main/graphql-types';

export const textSchema = gql`
    """
    Plain textual content meant to be directly consumed by humans.
    Examples: titles of problems, contests, etc.
    """
    type Text {
        "Best variant of this text for the given parameters (e.g., language)"
        # TODO: define parameters
        variant: String!
    }
`;

export class Text implements ApiOutputValue<'Text'> {
    constructor(readonly variants: TextVariant[]) {}

    variant() {
        return this.variants[0].value;
    }
}

export interface TextVariant {
    language?: string;
    value: string;
}
