import { gql } from 'apollo-server-core';

export const valenceSchema = gql`
    enum Valence {
        SUCCESS
        FAILURE
        PARTIAL
        NOMINAL
        SKIPPED
        IGNORED
        BLOCKED
    }
`;
