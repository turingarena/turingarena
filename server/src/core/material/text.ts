import { gql } from 'apollo-server-core';
import { Resolvers } from '../../generated/graphql-types';

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

export const textResolvers: Resolvers = {};
