import { gql } from 'apollo-server-core';
import { ApiOutputValue } from '../../main/graphql-types';
import { DateTimeColumn, DateTimeField } from './date-time';
import { FileColumn, FileField } from './file';
import { FulfillmentColumn, FulfillmentField } from './fulfillment';
import { HeaderColumn, HeaderField } from './header';
import { MemoryUsageColumn, MemoryUsageField } from './memory-usage';
import { MessageColumn, MessageField } from './message';
import { ScoreColumn, ScoreField } from './score';
import { TimeUsageColumn, TimeUsageField } from './time-usage';
import { Valence } from './valence';

export const fieldSchema = gql`
    "Container for values to show users as feedback, e.g., in table cells."
    union Field =
          ScoreField
        | FulfillmentField
        | MessageField
        | TimeUsageField
        | MemoryUsageField
        | HeaderField
        | DateTimeField
        | FileField

    "A column with a title."
    interface TitledColumn {
        title: Text!
    }

    "Definition of a table column."
    union Column =
          ScoreColumn
        | FulfillmentColumn
        | MessageColumn
        | TimeUsageColumn
        | MemoryUsageColumn
        | HeaderColumn
        | DateTimeColumn
        | FileColumn

    "Collection of fields, in 1-to-1 correspondence with a collection of columns."
    type Record {
        fields: [Field]!
        valence: Valence
    }

    type Table {
        columns: [Column!]!
        rows: [Record!]!
    }
`;

export type Field =
    | ScoreField
    | FulfillmentField
    | MessageField
    | TimeUsageField
    | MemoryUsageField
    | HeaderField
    | DateTimeField
    | FileField;

export type Column =
    | ScoreColumn
    | FulfillmentColumn
    | MessageColumn
    | TimeUsageColumn
    | MemoryUsageColumn
    | HeaderColumn
    | DateTimeColumn
    | FileColumn;

export class Record implements ApiOutputValue<'Record'> {
    __typename = 'Record' as const;

    constructor(readonly fields: Array<Field | null>, readonly valence: Valence | null) {}
}

export class ApiTable implements ApiOutputValue<'Table'> {
    __typename = 'Table' as const;

    constructor(readonly columns: Column[], readonly rows: Record[]) {}
}

export type ColumnGenerator<T> = [Column, (item: T) => Field | null | Promise<Field | null>];

export type TableGenerator<T> = Array<ColumnGenerator<T>>;

export function mapTable<TFrom, TTo>(
    generator: TableGenerator<TTo>,
    mapper: (item: TFrom) => TTo | null | Promise<TTo | null>,
): TableGenerator<TFrom> {
    return generator.map(
        ([column, cellMapper]): ColumnGenerator<TFrom> => [
            column,
            async item => {
                const mappedItem: TTo | null = await mapper(item);
                return mappedItem === null ? null : cellMapper(mappedItem);
            },
        ],
    );
}
