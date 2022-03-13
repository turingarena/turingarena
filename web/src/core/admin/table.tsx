import { gql } from '@apollo/client';
import { ValueFormatterParams, ValueGetterParams } from 'ag-grid-community';
import { AgGridColumn, AgGridReact } from 'ag-grid-react';
import { css, cx } from 'emotion';
import React from 'react';
import { ColumnFragment, FieldFragment, HeaderField, TableFragment } from '../../generated/graphql-types';
import { FragmentProps } from '../../util/fragment-props';
import { Field } from '../data/field';
import { Text } from '../data/text';
import { columnFragment, recordFragment } from '../field-table';

export const tableFragment = gql`
  fragment Table on Table {
    columns {
      ...Column
    }
    rows {
      ...Record
    }
  }

  ${recordFragment}
  ${columnFragment}
`;

export function Table({ data }: FragmentProps<TableFragment>) {
  return (
    <div
      className={cx(
        'ag-theme-alpine',
        css`
          flex: 1;
        `,
      )}
    >
      <AgGridReact rowData={data.rows.map(row => row.fields)}>
        {data.columns.map((column, i) => (
          <AgGridColumn
            field={String(i)}
            filter="text"
            resizable
            sortable
            headerName={column.title.variant}
            valueGetter={(params: ValueGetterParams) => getCellValue(column, params.data[i] as FieldFragment)}
            cellRendererFramework={(params: ValueFormatterParams) => <Field data={params.data[i] as FieldFragment} />}
          />
        ))}
      </AgGridReact>
    </div>
  );
}

function getCellValue(column: ColumnFragment, field: FieldFragment) {
  switch (column.__typename) {
    case 'HeaderColumn':
      return (field as HeaderField).index ?? (field as HeaderField).title.variant;
    default:
      return null;
  }
}
