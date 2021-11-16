import { gql } from 'apollo-server-core';

export const fieldSchema = gql`
    "Container for values to show users as feedback, e.g., in table cells."
    union Field = ScoreField | FulfillmentField | MessageField | TimeUsageField | MemoryUsageField | HeaderField

    "A column with a title."
    interface TitledColumn {
        title: Text!
    }

    "Definition of a table column."
    union Column = ScoreColumn | FulfillmentColumn | MessageColumn | TimeUsageColumn | MemoryUsageColumn | HeaderColumn

    "Collection of fields, in 1-to-1 correspondence with a collection of columns."
    type Record {
        fields: [Field!]!
        valence: Valence
    }

    type Table {
        columns: [Column!]!
        rows: [Record!]!
    }
`;
