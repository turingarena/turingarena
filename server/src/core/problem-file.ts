import { gql } from 'apollo-server-core';
import { Resolvers } from '../main/resolver-types';

export const problemFileSchema = gql`
    type ProblemFile {
        problem: Problem!
        path: String!
        content: FileContent!
    }
`;

export interface ProblemFileModelRecord {
    // ProblemFile: ProblemFile;
}

export const problemFileResolvers: Resolvers = {
    ProblemFile: {
        // content: file => file.getContent(),
        // problem: file => file.getProblem(),
    },
};
