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
        fieldIndex: Int!
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

    static async fromColumnDefinitions<T>(
        columns: TableDefinition<T>,
        items: T[],
        valenceMapper?: (item: T) => Valence | null,
    ) {
        return new ApiTable(getTableColumns(columns), await getTableRows<T>(columns, items, valenceMapper));
    }
}

export async function getTableRows<T>(
    columns: TableDefinition<T>,
    items: T[],
    valenceMapper?: (item: T) => Valence | null,
) {
    return Promise.all(
        items.map(
            async item =>
                new Record(
                    await Promise.all(columns.map(async ({ dataMapper: mapper }) => mapper(item))),
                    valenceMapper?.(item) ?? null,
                ),
        ),
    );
}

export function getTableColumns(columns: TableDefinition<never>) {
    return columns.map(({ columnMapper }, i) => columnMapper(i));
}

export type ColumnDefinition<T> = {
    columnMapper: (fieldIndex: number) => Column;
    dataMapper: (item: T) => Field | null | Promise<Field | null>;
};

export type TableDefinition<T> = Array<ColumnDefinition<T>>;

export function mapTable<TFrom, TTo>(
    generator: TableDefinition<TTo>,
    itemMapper: (item: TFrom) => TTo | null | Promise<TTo | null>,
): TableDefinition<TFrom> {
    return generator.map(
        ({ dataMapper, ...rest }): ColumnDefinition<TFrom> => ({
            dataMapper: async item => {
                const mappedItem: TTo | null = await itemMapper(item);
                return mappedItem === null ? null : dataMapper(mappedItem);
            },
            ...rest,
        }),
    );
}
