import { gql } from 'apollo-server-core';

export const headerSchema = gql`
    "Field serving as header for a row containing a numeric index associated with the row."
    type IndexField {
        index: Int!
    }

    "Column containing row headers with a numeric index associated with each row."
    type IndexColumn implements TitledColumn {
        title: Text!
    }

    "Field serving as header for a row containing a title associated with the row."
    type TitleField {
        title: Text!
    }

    "Column containing row headers with a title associated with each row."
    type TitleColumn implements TitledColumn {
        title: Text!
    }
`;
