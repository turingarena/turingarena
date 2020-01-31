import { Component, Input, ViewEncapsulation } from '@angular/core';
import { ColDef } from 'ag-grid-community';
import gql from 'graphql-tag';
import { FeedbackTableColumnFragment, FeedbackTableRecordFragment } from '../generated/graphql-types';
import { check, fail, unexpected } from '../util/check';
import { fulfillmentVariableFragment } from './grading/fulfillment-field.component';
import { scoreVariableFragment } from './grading/score-field.component';
import { textFragment } from './material/text.pipe';

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
    return [
      ...columns.map(
        (c, i): ColDef => ({
          colId: `custom.${i}`,
          headerName: c.title.variant,
          // FIXME: generated types should not allow undefineds
          // tslint:disable-next-line: no-null-undefined-union
          valueGetter: ({ data }) => {
            const record = data as FeedbackTableRecordFragment;
            const f = record.fields[i];

            switch (c.__typename) {
              case 'FulfillmentColumn':
                check(f.__typename === 'FulfillmentField', `expected FulfillmentField, got ${f.__typename}`);

                return f.fulfilled;
              case 'ScoreColumn':
                check(f.__typename === 'ScoreField', `expected ScoreField, got ${f.__typename}`);

                return f.score;
              case 'IndexHeaderColumn':
                check(f.__typename === 'IndexHeaderField', `expected IndexHeaderField, got ${f.__typename}`);

                return f.index;
              case 'TitleHeaderColumn':
                check(f.__typename === 'TitleHeaderField', `expected TitleHeaderField, got ${f.__typename}`);

                return f.title;
              case 'TimeUsageColumn':
                check(f.__typename === 'TimeUsageField', `expected TimeUsageField, got ${f.__typename}`);

                return f.timeUsage?.seconds;
              case 'MemoryUsageColumn':
                check(f.__typename === 'MemoryUsageField', `expected MemoryUsageField, got ${f.__typename}`);

                return f.memoryUsage?.bytes;
              case 'MessageColumn':
                check(f.__typename === 'MessageField', `expected MessageField, got ${f.__typename}`);

                return f.message?.variant;
              case undefined:
                // FIXME: generated types should not allow undefineds
                fail('column has no typename');
              default:
                unexpected(c);
            }
          },
        }),
      ),
    ];
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

  fragment FeedbackTableRecord on Record {
    fields {
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
  }

  ${scoreVariableFragment}
  ${fulfillmentVariableFragment}
  ${textFragment}
`;
