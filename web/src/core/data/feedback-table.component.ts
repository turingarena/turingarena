import { Component, Input, TemplateRef, ViewChild, ViewEncapsulation } from '@angular/core';
import { ColDef, ValueGetterParams } from 'ag-grid-community';
import gql from 'graphql-tag';
import {
  FeedbackTableColumnFragment,
  FeedbackTableRecordFragment,
  FieldFragment,
  FulfillmentColumn,
  IndexColumn,
  MemoryUsageColumn,
  MessageColumn,
  ScoreColumn,
  TimeUsageColumn,
  TitleColumn,
} from '../../generated/graphql-types';
import { check } from '../../util/check';
import { TemplateCellRendererComponent } from '../../util/template-cell-renderer.component';
import { fulfillmentVariableFragment } from '../grading/fulfillment-field.component';
import { scoreVariableFragment } from '../grading/score-field.component';
import { textFragment } from '../material/text.pipe';
import { fieldFragment } from './field.component';

export interface ColumnDefinition {
  def: ColDef;
  mainClasses?: string[];
  getCellData(
    field: FieldFragment,
  ): {
    value: unknown;
    tooltip?: string;
  };
}

export class ColumnMeta<T extends FeedbackTableColumnFragment> {
  constructor(readonly typename: T['__typename'], readonly createColumnDefinition: (column: T) => ColumnDefinition) {}
}

const metas = [
  new ColumnMeta<FulfillmentColumn>('FulfillmentColumn', c => ({
    def: {
      sortable: true,
      filter: 'agNumberColumnFilter',
    },
    mainClasses: ['numeric-cell'],
    getCellData: field => {
      check(field.__typename === 'FulfillmentField', `expected FulfillmentField, got ${field.__typename}`);

      return {
        value: field.fulfilled,
        tooltip: field.fulfilled !== null ? `${c.title.variant}: ${field.fulfilled ? 'Yes' : 'No'}` : undefined,
      };
    },
  })),
  new ColumnMeta<ScoreColumn>('ScoreColumn', c => ({
    def: {
      sortable: true,
      filter: 'agNumberColumnFilter',
    },
    mainClasses: ['numeric-cell'],
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
  new ColumnMeta<IndexColumn>('IndexColumn', c => ({
    def: {
      sortable: true,
      filter: 'agNumberColumnFilter',
    },
    mainClasses: ['numeric-cell'],
    getCellData: field => {
      check(field.__typename === 'IndexField', `expected IndexField, got ${field.__typename}`);

      return {
        value: field.index,
        tooltip: `${c.title.variant} ${field.index}`,
      };
    },
  })),
  new ColumnMeta<TitleColumn>('TitleColumn', c => ({
    def: {
      sortable: true,
      filter: 'agTextColumnFilter',
    },
    getCellData: field => {
      check(field.__typename === 'TitleField', `expected TitleField, got ${field.__typename}`);

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
    mainClasses: ['numeric-cell'],
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
    mainClasses: ['numeric-cell'],
    getCellData: field => {
      check(field.__typename === 'MemoryUsageField', `expected MemoryUsageField, got ${field.__typename}`);

      return { value: field.memoryUsage?.bytes ?? null };
    },
  })),
  new ColumnMeta<MessageColumn>('MessageColumn', c => ({
    def: {
      filter: 'agTextColumnFilter',
    },
    getCellData: field => {
      check(field.__typename === 'MessageField', `expected MessageField, got ${field.__typename}`);

      return { value: field.message?.variant ?? null };
    },
  })),
];

@Component({
  selector: 'app-feedback-table',
  templateUrl: './feedback-table.component.html',
  styleUrls: ['./feedback-table.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class FeedbackTableComponent {
  @Input()
  columns!: FeedbackTableColumnFragment[];

  @Input()
  records!: FeedbackTableRecordFragment[];

  @ViewChild('cellRendererTemplate', { static: true })
  cellRendererTemplate!: TemplateRef<unknown>;

  getColumns = (columns: FeedbackTableColumnFragment[]): ColDef[] =>
    columns.map(
      (c, i): ColDef => {
        const meta = metas.find(m => m.typename === c.__typename) as ColumnMeta<typeof c>;
        const { def, mainClasses, getCellData } = meta.createColumnDefinition(c);

        function getField({ data }: { data?: unknown }) {
          return (data as FeedbackTableRecordFragment).fields[i];
        }

        return {
          colId: `custom.${i}`,
          headerName: c.title.variant,
          resizable: true,

          valueGetter: params => getCellData(getField(params)).value,
          tooltip: params => getCellData(getField(params)).tooltip ?? '',
          cellClass: params => {
            const field = getField(params);
            if ('valence' in field) {
              return [...(mainClasses ?? []), `valence-${field.valence}`];
            } else {
              return [...(mainClasses ?? [])];
            }
          },
          // tooltipValueGetter: params => getCellData(getField(params)).tooltip ?? '',
          cellRendererFramework: TemplateCellRendererComponent,
          cellRendererParams: (params: ValueGetterParams) => ({
            template: this.cellRendererTemplate,
            field: getField(params),
          }),
          ...def,
        };
      },
    );
}

export const feedbackTableFragment = gql`
  fragment FeedbackTableColumn on Column {
    ... on TitledColumn {
      title {
        ...Text
      }
    }
  }

  fragment FeedbackTableRecord on Record {
    fields {
      ...Field
      ... on HasValence {
        valence
      }
    }
  }

  ${scoreVariableFragment}
  ${fulfillmentVariableFragment}
  ${fieldFragment}
  ${textFragment}
`;
