import { gql } from '@apollo/client';
import { ColDef, ValueFormatterParams, ValueGetterParams } from 'ag-grid-community';
import { AgGridColumn, AgGridReact } from 'ag-grid-react';
import { css, cx } from 'emotion';
import React from 'react';
import {
  ColumnFragment,
  FieldFragment,
  FulfillmentFieldFragment,
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
      <AgGridReact
        rowData={data.rows.map(row => row.fields)}
        multiSortKey="ctrl"
        onGridReady={event => {
          event.api.sizeColumnsToFit();
        }}
      >
        {data.columns.map((column, i) => (
          <AgGridColumn
            id={String(column.fieldIndex)}
            headerName={column.title.variant}
            resizable
            sortable
            {...getAgGridColDef(column)}
            cellRendererFramework={(params: ValueFormatterParams) => {
              const field = params.data[column.fieldIndex] as FieldFragment | null;
              return field && <Field data={field} />;
            }}
          />
        ))}
      </AgGridReact>
    </div>
  );
}

function getAgGridColDef(column: ColumnFragment): ColDef {
  switch (column.__typename) {
    case 'HeaderColumn':
      return {
        valueGetter: (params: ValueGetterParams) =>
          (params.data[column.fieldIndex] as HeaderFieldFragment | null)?.index ??
          (params.data[column.fieldIndex] as HeaderFieldFragment | null)?.title?.variant,
      };
    case 'ScoreColumn':
      return {
        filter: 'number',
        valueGetter: (params: ValueGetterParams) =>
          (params.data[column.fieldIndex] as ScoreFieldFragment | null)?.score ?? null,
      };
    case 'FulfillmentColumn':
      return {
        filter: 'number',
        valueGetter: (params: ValueGetterParams) => {
          const fulfilled = (params.data[column.fieldIndex] as FulfillmentFieldFragment | null)?.fulfilled ?? null;
          if (fulfilled === null) return null;
          return fulfilled ? 1 : 0;
        },
      };
    case 'DateTimeColumn':
      return {};
    default:
      return { filter: 'text' };
  }
}
