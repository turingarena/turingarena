import { Component, Input, ViewEncapsulation } from '@angular/core';
import { ColDef } from 'ag-grid-community';
import gql from 'graphql-tag';
import { FeedbackTableColumnFragment, FeedbackTableRecordFragment } from '../generated/graphql-types';
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
  columns!: FeedbackTableColumnFragment;

  @Input()
  records!: FeedbackTableRecordFragment;

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

            if (c.__typename === 'FulfillmentColumn' && f.__typename === 'FulfillmentField') return f.fulfilled;
            if (c.__typename === 'ScoreColumn' && f.__typename === 'ScoreField') return f.score;
            if (c.__typename === 'IndexHeaderColumn' && f.__typename === 'IndexHeaderField') return f.index;
            if (c.__typename === 'TitleHeaderColumn' && f.__typename === 'TitleHeaderField') return f.title;
            if (c.__typename === 'TimeUsageColumn' && f.__typename === 'TimeUsageField') return undefined;
            if (c.__typename === 'MemoryUsageColumn' && f.__typename === 'MemoryUsageField') return undefined;
            if (c.__typename === 'MessageColumn' && f.__typename === 'MessageField') {
              return f.message !== null ? f.message.variant : null;
            }

            throw new Error(`Invalid or unsupported field ${f.__typename} in column ${c.__typename}`);
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
