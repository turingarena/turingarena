import { gql } from '@apollo/client';
import { ValueFormatterParams, ValueGetterParams } from 'ag-grid-community';
import { AgGridColumn, AgGridReact } from 'ag-grid-react';
import { css, cx } from 'emotion';
import React from 'react';
import {
  ColumnFragment,
  DateTimeFieldFragment,
  FieldFragment,
  HeaderFieldFragment,
  ScoreFieldFragment,
  TableFragment,
} from '../../generated/graphql-types';
import { FragmentProps } from '../../util/fragment-props';
import { Field } from '../data/field';
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
            filter={getFilterMode(column)}
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

function getFilterMode(column: ColumnFragment): 'set' | 'number' | 'text' | 'date' | null {
  switch (column.__typename) {
    case 'ScoreColumn':
      return 'number';
    case 'DateTimeColumn':
      return null;
    default:
      return 'text';
  }
}

function getCellValue(column: ColumnFragment, field: FieldFragment) {
  switch (column.__typename) {
    case 'HeaderColumn':
      return (field as HeaderFieldFragment).index ?? (field as HeaderFieldFragment).title.variant;
    case 'ScoreColumn':
      return (field as ScoreFieldFragment).score;
    case 'DateTimeColumn':
      const { dateTime } = field as DateTimeFieldFragment;
      return dateTime === null ? null : new Date(dateTime.local);
    default:
      return null;
  }
}
