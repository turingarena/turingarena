import { gql } from 'apollo-server-core';
import { Resolvers } from '../generated/graphql-types';

export const problemSchema = gql`
    type Problem {
        name: ID!
        files: [File!]!
    }

    input ProblemInput {
        name: ID!
        files: [ID!]!
    }
`;

export const problemResolvers: Resolvers = {
    Problem: {
        files: problem => problem.getFiles(),
    },
};
