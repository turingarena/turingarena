import { gql } from '@apollo/client';
import { AgGridColumn, AgGridReact } from 'ag-grid-react';
import { css, cx } from 'emotion';
import React from 'react';
import { FieldFragment, TableFragment } from '../../generated/graphql-types';
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
            resizable
            sortable
            headerComponent={() => <Text data={column.title} />}
            cellRendererFramework={({ value }: { value: FieldFragment }) => <Field data={value} />}
          />
        ))}
      </AgGridReact>
    </div>
  );
}
