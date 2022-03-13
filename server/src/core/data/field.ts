import { gql } from 'apollo-server-core';
import { ApiOutputValue } from '../../main/graphql-types';
import { Valence } from './valence';
import { ScoreField, ScoreColumn } from './score';
import { FulfillmentField, FulfillmentColumn } from './fulfillment';
import { MessageField, MessageColumn } from './message';
import { TimeUsageField, TimeUsageColumn } from './time-usage';
import { MemoryUsageField, MemoryUsageColumn } from './memory-usage';
import { HeaderField, HeaderColumn } from './header';

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

export type Field = ScoreField | FulfillmentField | MessageField | TimeUsageField | MemoryUsageField | HeaderField;
export type Column =
    | ScoreColumn
    | FulfillmentColumn
    | MessageColumn
    | TimeUsageColumn
    | MemoryUsageColumn
    | HeaderColumn;

export class Record implements ApiOutputValue<'Record'> {
    __typename = 'Record' as const;

    constructor(readonly fields: Field[], readonly valence: Valence | null) {}
}

export class ApiTable implements ApiOutputValue<'Table'> {
    __typename = 'Table' as const;

    constructor(readonly columns: Column[], readonly rows: Record[]) {}
}
