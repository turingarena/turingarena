import { Component, Input, TemplateRef, ViewChild, ViewEncapsulation } from '@angular/core';
import { ColDef, ValueGetterParams } from 'ag-grid-community';
import gql from 'graphql-tag';
import {
  FeedbackTableColumnFragment,
  FeedbackTableFieldFragment,
  FeedbackTableRecordFragment,
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
import { indexFieldFragment } from './index-field.component';
import { memoryUsageFieldFragment } from './memory-usage-field.component';
import { messageFieldFragment } from './message-field.component';
import { timeUsageFieldFragment } from './time-usage-field.component';
import { titleFieldFragment } from './title-field.component';

export interface ColumnDefinition {
  def: ColDef;
  getCellData(
    field: FeedbackTableFieldFragment,
  ): {
    value: unknown;
  };
}

export class ColumnMeta<T extends FeedbackTableColumnFragment> {
  constructor(readonly typename: T['__typename'], readonly createColumnDefinition: (column: T) => ColumnDefinition) {}
}

const metas = [
  new ColumnMeta<FulfillmentColumn>('FulfillmentColumn', c => ({
    def: {},
    getCellData: field => {
      check(field.__typename === 'FulfillmentField', `expected FulfillmentField, got ${field.__typename}`);

      return { value: field.fulfilled };
    },
  })),
  new ColumnMeta<ScoreColumn>('ScoreColumn', c => ({
    def: {},
    getCellData: field => {
      check(field.__typename === 'ScoreField', `expected ScoreField, got ${field.__typename}`);

      return { value: field.score };
    },
  })),
  new ColumnMeta<IndexColumn>('IndexColumn', c => ({
    def: {},
    getCellData: field => {
      check(field.__typename === 'IndexField', `expected IndexField, got ${field.__typename}`);

      return { value: field.index };
    },
  })),
  new ColumnMeta<TitleColumn>('TitleColumn', c => ({
    def: {},
    getCellData: field => {
      check(field.__typename === 'TitleField', `expected TitleField, got ${field.__typename}`);

      return { value: field.title };
    },
  })),
  new ColumnMeta<TimeUsageColumn>('TimeUsageColumn', c => ({
    def: {},
    getCellData: field => {
      check(field.__typename === 'TimeUsageField', `expected TimeUsageField, got ${field.__typename}`);

      return { value: field.timeUsage?.seconds ?? null };
    },
  })),
  new ColumnMeta<MemoryUsageColumn>('MemoryUsageColumn', c => ({
    def: {},
    getCellData: field => {
      check(field.__typename === 'MemoryUsageField', `expected MemoryUsageField, got ${field.__typename}`);

      return { value: field.memoryUsage?.bytes ?? null };
    },
  })),
  new ColumnMeta<MessageColumn>('MessageColumn', c => ({
    def: {},
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
        const { def, getCellData } = meta.createColumnDefinition(c);

        function getField({ data }: ValueGetterParams) {
          return (data as FeedbackTableRecordFragment).fields[i];
        }

        return {
          colId: `custom.${i}`,
          headerName: c.title.variant,
          valueGetter: params => getCellData(getField(params)).value,
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

  fragment FeedbackTableField on Field {
    ... on FulfillmentField {
      ...FulfillmentField
    }
    ... on ScoreField {
      ...ScoreField
    }
    ... on IndexField {
      ...IndexField
    }
    ... on TitleField {
      ...TitleField
    }
    ... on MessageField {
      ...MessageField
    }
    ... on TimeUsageField {
      ...TimeUsageField
    }
    ... on MemoryUsageField {
      ...MemoryUsageField
    }
  }

  fragment FeedbackTableRecord on Record {
    fields {
      ...FeedbackTableField
    }
  }

  ${scoreVariableFragment}
  ${fulfillmentVariableFragment}
  ${memoryUsageFieldFragment}
  ${timeUsageFieldFragment}
  ${messageFieldFragment}
  ${titleFieldFragment}
  ${indexFieldFragment}
  ${textFragment}
`;
