import { gql } from '@apollo/client';
import { ColDef, ValueFormatterParams, ValueGetterParams } from 'ag-grid-community';
import { AgGridColumn, AgGridReact } from 'ag-grid-react';
import { css, cx } from 'emotion';
import React, { useRef } from 'react';
import {
  ColumnFragment,
  ColumnGroupItemShow,
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
  /* Avoids losing state. FIXME: find a better solution (columns may change in fact) */
  const { current: columns } = useRef(mapColumns(data.columns));

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
        defaultColDef={{
          width: 120,
        }}
      >
        {columns}
      </AgGridReact>
    </div>
  );
}

function mapColumns(columns: ColumnFragment[]) {
  return columns.map(column => mapColumn(column));
}

function mapColumn(column: ColumnFragment, columnGroupShow: ColumnGroupItemShow = 'ALWAYS'): JSX.Element {
  const columnGroupShow2 =
    columnGroupShow === 'ALWAYS' ? undefined : columnGroupShow === 'WHEN_OPEN' ? 'open' : 'closed';

  return column.__typename === 'GroupColumn' ? (
    <AgGridColumn
      id={column.title.variant /* FIXME */}
      groupId={column.title.variant /* FIXME */}
      headerName={column.title.variant}
      columnGroupShow={columnGroupShow2}
      resizable
    >
      {column.children.map(({ show, column }) => mapColumn(column as ColumnFragment, show))}
    </AgGridColumn>
  ) : (
    <AgGridColumn
      id={String(column.fieldIndex)}
      headerName={column.title.variant}
      resizable
      sortable
      columnGroupShow={columnGroupShow2}
      {...getAgGridColDef(column)}
      cellRendererFramework={(params: ValueFormatterParams) => {
        const field = params.data[column.fieldIndex] as FieldFragment | null;
        return field && <Field data={field} />;
      }}
    />
  );
}

function getAgGridColDef(column: ColumnFragment): ColDef {
  switch (column.__typename) {
    case 'HeaderColumn':
      return {
        filter: 'text',
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
