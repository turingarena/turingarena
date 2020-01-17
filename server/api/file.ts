import { gql } from 'apollo-server-core';

export const fileSchema = gql`
    type File {
        hash: ID!
        fileName: String!
        type: String!
        contentBase64: String!
    }

    input FileInput {
        fileName: String!
        type: String!
        contentBase64: String!
    }
`;

// TODO: resolvers to add and retrieve files
