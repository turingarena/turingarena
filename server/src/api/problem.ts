import { gql } from 'apollo-server-core';

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
