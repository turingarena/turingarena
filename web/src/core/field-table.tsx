import { gql } from '@apollo/client';
import { ColDef, ICellRendererParams } from 'ag-grid-community';
import { css, cx } from 'emotion';
import React from 'react';
import {
  ColumnFragment,
  FieldFragment,
  FulfillmentColumn,
  HeaderColumn,
  MemoryUsageColumn,
  MessageColumn,
  RecordFragment,
  ScoreColumn,
  TimeUsageColumn,
  Valence,
} from '../generated/graphql-types';
import { check } from '../util/check';
import { Field, fieldFragment } from './fields/field';
import { textFragment } from './text';

export interface ColumnDefinition {
  def: ColDef;
  mainClass?: string;
  getCellData(
    field: FieldFragment,
  ): {
    value: unknown;
    tooltip?: string;
  };
}

const cellValenceSuccessCss = 'table-success';
const cellValenceDangerCss = 'table-danger';
const cellValenceWarningCss = 'table-warning';

function getCellClassByValence(valence: Valence | null) {
  switch (valence) {
    case 'SUCCESS':
      return cellValenceSuccessCss;
    case 'PARTIAL':
    case 'WARNING':
      return cellValenceWarningCss;
    case 'FAILURE':
      return cellValenceDangerCss;
    default:
      return undefined;
  }
}

export class ColumnMeta<T extends ColumnFragment> {
  constructor(readonly typename: T['__typename'], readonly createColumnDefinition: (column: T) => ColumnDefinition) {}
}

const numericCellCss = css`
  text-align: right;
`;

const metas = [
  new ColumnMeta<FulfillmentColumn>('FulfillmentColumn', c => ({
    def: {
      sortable: true,
      filter: 'agNumberColumnFilter',
    },
    mainClass: css`
      text-align: center;
    `,
    getCellData: field => {
      check(field.__typename === 'FulfillmentField', `expected FulfillmentField, got ${field.__typename}`);

      return {
        value: field.fulfilled !== null ? (field.fulfilled ? 1 : 0) : null,
        tooltip: field.fulfilled !== null ? `${c.title.variant}: ${field.fulfilled ? 'Yes' : 'No'}` : undefined,
      };
    },
  })),
  new ColumnMeta<ScoreColumn>('ScoreColumn', c => ({
    def: {
      sortable: true,
      filter: 'agNumberColumnFilter',
    },
    mainClass: numericCellCss,
    getCellData: field => {
      check(field.__typename === 'ScoreField', `expected ScoreField, got ${field.__typename}`);

      return {
        value: field.score,
        tooltip:
          field.score !== null
            ? `${c.title.variant}: ${field.score.toFixed(field.scoreRange.decimalDigits)} points`
            : undefined,
      };
    },
  })),
  new ColumnMeta<HeaderColumn>('HeaderColumn', c => ({
    def: {
      sortable: true,
      filter: 'agTextColumnFilter',
    },
    getCellData: field => {
      check(field.__typename === 'HeaderField', `expected HeaderField, got ${field.__typename}`);

      return {
        value: field.title,
        tooltip: `${c.title.variant} ${field.title.variant}`,
      };
    },
  })),
  new ColumnMeta<TimeUsageColumn>('TimeUsageColumn', c => ({
    def: {
      sortable: true,
      filter: 'agNumberColumnFilter',
    },
    mainClass: numericCellCss,
    getCellData: field => {
      check(field.__typename === 'TimeUsageField', `expected TimeUsageField, got ${field.__typename}`);

      return { value: field.timeUsage?.seconds ?? null };
    },
  })),
  new ColumnMeta<MemoryUsageColumn>('MemoryUsageColumn', c => ({
    def: {
      sortable: true,
      filter: 'agNumberColumnFilter',
    },
    mainClass: numericCellCss,
    getCellData: field => {
      check(field.__typename === 'MemoryUsageField', `expected MemoryUsageField, got ${field.__typename}`);

      return { value: field.memoryUsage?.bytes ?? null };
    },
  })),
  new ColumnMeta<MessageColumn>('MessageColumn', c => ({
    def: {
      filter: 'agTextColumnFilter',
      flex: 1,
    },
    getCellData: field => {
      check(field.__typename === 'MessageField', `expected MessageField, got ${field.__typename}`);

      return { value: field.message?.variant ?? null };
    },
  })),
];

export const getFieldColumns = <T extends {}>(
  columns: ColumnFragment[],
  recordExtractor: (data: T) => RecordFragment,
): ColDef[] =>
  columns.map(
    (c, i): ColDef => {
      const meta = metas.find(m => m.typename === c.__typename) as ColumnMeta<typeof c>;
      const { def, mainClass: mainClasses, getCellData } = meta.createColumnDefinition(c);

      function getField({ data }: { data?: T }) {
        return recordExtractor(data!).fields[i];
      }

      return {
        colId: `custom.${i}`,
        headerName: c.title.variant,
        resizable: true,
        width: 100,

        valueGetter: params => getCellData(getField(params)).value,
        tooltipValueGetter: params => getCellData(getField(params)).tooltip ?? '',
        cellClass: params => {
          const field = getField(params);

          return cx(mainClasses, getCellClassByValence('valence' in field ? field.valence : null));
        },
        cellRendererFramework: (props: ICellRendererParams) => <Field data={getField(props)} />,
        ...def,
      };
    },
  );

export const columnFragment = gql`
  fragment Column on Column {
    ... on TitledColumn {
      title {
        ...Text
      }
    }
  }

  ${textFragment}
`;

export const recordFragment = gql`
  fragment Record on Record {
    fields {
      ...Field
      ... on HasValence {
        valence
      }
    }
  }

  ${fieldFragment}
`;
