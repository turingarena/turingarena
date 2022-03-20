import { gql } from 'apollo-server-core';
import { ApiOutputValue } from '../../main/graphql-types';
import { DateTimeColumn, DateTimeField } from './date-time';
import { FileColumn, FileField } from './file';
import { FulfillmentColumn, FulfillmentField } from './fulfillment';
import { HeaderColumn, HeaderField } from './header';
import { MemoryUsageColumn, MemoryUsageField } from './memory-usage';
import { MessageColumn, MessageField } from './message';
import { ScoreColumn, ScoreField } from './score';
import { Text } from './text';
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

    "A column grouping more columns"
    type GroupColumn {
        title: Text!
        children: [ColumnGroupItem!]!
    }

    type ColumnGroupItem {
        show: ColumnGroupItemShow!
        column: Column!
    }

    enum ColumnGroupItemShow {
        ALWAYS
        WHEN_OPEN
        WHEN_CLOSED
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
        | GroupColumn

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

export type AtomicColumn =
    | ScoreColumn
    | FulfillmentColumn
    | MessageColumn
    | TimeUsageColumn
    | MemoryUsageColumn
    | HeaderColumn
    | DateTimeColumn
    | FileColumn;

export type Column = AtomicColumn | GroupColumn;

export class GroupColumn implements ApiOutputValue<'GroupColumn'> {
    constructor(readonly title: Text, readonly children: Array<{ show: ColumnGroupItemShow; column: Column }>) {}

    __typename = 'GroupColumn' as const;
}

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
    tableDefinition: TableDefinition<T>,
    items: T[],
    valenceMapper?: (item: T) => Valence | null,
) {
    const columns = flattenTableDefinition(tableDefinition);

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

function flattenTableDefinition<T>(tableDefinition: TableDefinition<T>): Array<AtomicColumnDefinition<T>> {
    return tableDefinition.flatMap(column =>
        column instanceof AtomicColumnDefinition
            ? [column]
            : flattenTableDefinition(column.children.map(x => x.column)),
    );
}

export function getTableColumns(tableDefinition: TableDefinition<never>) {
    let index = -1;

    function getLevel(column: ColumnDefinition<never>): Column {
        return column instanceof AtomicColumnDefinition
            ? column.columnMapper((index += 1))
            : new GroupColumn(
                  column.title,
                  column.children.map(child => ({ show: child.show, column: getLevel(child.column) })),
              );
    }

    return tableDefinition.map(getLevel);
}

export class AtomicColumnDefinition<T> {
    constructor(
        readonly columnMapper: (fieldIndex: number) => AtomicColumn,
        readonly dataMapper: (item: T) => Field | null | Promise<Field | null>,
    ) {}
}

export type ColumnGroupItemShow = ApiOutputValue<'ColumnGroupItemShow'>;

export class GroupColumnDefinition<T> {
    constructor(
        readonly title: Text,
        readonly children: Array<{ show: ColumnGroupItemShow; column: ColumnDefinition<T> }>,
    ) {}
}

export type ColumnDefinition<T> = AtomicColumnDefinition<T> | GroupColumnDefinition<T>;

export type TableDefinition<T> = Array<ColumnDefinition<T>>;

export function mapTable<TFrom, TTo>(
    tableDefinition: TableDefinition<TTo>,
    itemMapper: (item: TFrom) => TTo | null | Promise<TTo | null>,
): TableDefinition<TFrom> {
    return tableDefinition.map(x => mapColumn(x, itemMapper));
}

export function mapColumn<TFrom, TTo>(
    column: ColumnDefinition<TTo>,
    itemMapper: (item: TFrom) => TTo | null | Promise<TTo | null>,
): ColumnDefinition<TFrom> {
    if (column instanceof AtomicColumnDefinition) {
        const { dataMapper, columnMapper } = column;
        return new AtomicColumnDefinition<TFrom>(columnMapper, async item => {
            const mappedItem: TTo | null = await itemMapper(item);
            return mappedItem === null ? null : dataMapper(mappedItem);
        });
    } else {
        return new GroupColumnDefinition<TFrom>(
            column.title,
            column.children.map(child => ({ show: child.show, column: mapColumn(child.column, itemMapper) })),
        );
    }
}
