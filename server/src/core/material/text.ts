import { gql } from 'apollo-server-core';
import { Resolvers } from '../../main/resolver-types';

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

export type Text = TextVariant[];

export interface TextVariant {
    language?: string;
    value: string;
}

export interface TextModelRecord {
    Text: Text;
}

export const textResolvers: Resolvers = {
    Text: {
        variant: text => text[0].value,
    },
};
