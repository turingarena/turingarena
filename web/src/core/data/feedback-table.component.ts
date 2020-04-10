import { Component, Input, ViewEncapsulation } from '@angular/core';
import { ColDef, ValueGetterParams } from 'ag-grid-community';
import gql from 'graphql-tag';
import {
  FeedbackTableColumnFragment,
  FeedbackTableFieldFragment,
  FeedbackTableRecordFragment,
  FulfillmentColumn,
  IndexHeaderColumn,
  MemoryUsageColumn,
  MessageColumn,
  ScoreColumn,
  TimeUsageColumn,
  TitleHeaderColumn,
} from '../../generated/graphql-types';
import { check } from '../../util/check';
import { fulfillmentVariableFragment } from '../grading/fulfillment-field.component';
import { scoreVariableFragment } from '../grading/score-field.component';
import { textFragment } from '../material/text.pipe';

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
  new ColumnMeta<IndexHeaderColumn>('IndexHeaderColumn', c => ({
    def: {},
    getCellData: field => {
      check(field.__typename === 'IndexHeaderField', `expected IndexHeaderField, got ${field.__typename}`);

      return { value: field.index };
    },
  })),
  new ColumnMeta<TitleHeaderColumn>('TitleHeaderColumn', c => ({
    def: {},
    getCellData: field => {
      check(field.__typename === 'TitleHeaderField', `expected TitleHeaderField, got ${field.__typename}`);

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

  getColumns(columns: FeedbackTableColumnFragment[]): ColDef[] {
    return columns.map(
      (c, i): ColDef => {
        const meta = metas.find(m => m.typename === c.__typename) as ColumnMeta<typeof c>;
        const { def, getCellData } = meta.createColumnDefinition(c);

        function cellData({ data }: ValueGetterParams) {
          return getCellData((data as FeedbackTableRecordFragment).fields[i]);
        }

        return {
          colId: `custom.${i}`,
          headerName: c.title.variant,
          valueGetter: params => cellData(params).value,
          ...def,
        };
      },
    );
  }
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
    ... on IndexHeaderField {
      index
    }
    ... on TitleHeaderField {
      title {
        ...Text
      }
    }
    ... on MessageField {
      message {
        ...Text
      }
    }
    ... on TimeUsageField {
      timeUsage {
        seconds
      }
    }
    ... on MemoryUsageField {
      memoryUsage {
        bytes
      }
    }
  }

  fragment FeedbackTableRecord on Record {
    fields {
      ...FeedbackTableField
    }
  }

  ${scoreVariableFragment}
  ${fulfillmentVariableFragment}
  ${textFragment}
`;
