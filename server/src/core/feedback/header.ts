import { gql } from 'apollo-server-core';

export const headerSchema = gql`
    "Field serving as header (e.g., for a row) containing a title and optionally a numeric index (e.g., for sorting)."
    type HeaderField {
        title: Text!
        index: Int
    }

    "Column containing headers for each row."
    type HeaderColumn implements TitledColumn {
        title: Text!
    }
`;
