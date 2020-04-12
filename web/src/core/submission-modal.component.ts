import { Component, Input, OnChanges, ViewEncapsulation } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { Apollo, QueryRef } from 'apollo-angular';
import gql from 'graphql-tag';
import { Observable } from 'rxjs';
import { map, tap } from 'rxjs/operators';
import {
  RecordFragment,
  SubmissionModalFragment,
  SubmissionQuery,
  SubmissionQueryVariables,
} from '../generated/graphql-types';
import { columnFragment, getFieldColumns, recordFragment } from './data/field-table';
import { textFragment } from './material/text.pipe';

@Component({
  selector: 'app-submission-modal',
  templateUrl: './submission-modal.component.html',
  styleUrls: ['./submission-modal.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class SubmissionModalComponent implements OnChanges {
  constructor(private readonly apollo: Apollo) {}

  @Input()
  modal!: NgbActiveModal;

  @Input()
  id!: string;

  queryRef!: QueryRef<SubmissionQuery, SubmissionQueryVariables>;
  dataObservable!: Observable<SubmissionQuery>;

  ngOnChanges() {
    this.queryRef = this.apollo.watchQuery<SubmissionQuery, SubmissionQueryVariables>({
      query: gql`
        query Submission($id: ID!) {
          submission(id: $id) {
            ...SubmissionModal
          }
        }

        ${submissionModalFragment}
      `,
      variables: {
        id: this.id,
      },
      pollInterval: 500,
    });
    this.dataObservable = this.queryRef.valueChanges.pipe(
      map(({ data }) => data),
      tap(data => {
        if (data.submission.officialEvaluation?.status !== 'PENDING') {
          this.queryRef.stopPolling();
        }
      }),
    );
  }

  getColumns(data: SubmissionModalFragment) {
    return getFieldColumns(data.feedbackTable.columns, (row: RecordFragment) => row);
  }
}

export const submissionModalFragment = gql`
  fragment SubmissionModal on Submission {
    id
    # TODO: files
    createdAt {
      local
    }
    officialEvaluation {
      status
    }
    problem {
      id
      title {
        ...Text
      }
    }
    feedbackTable {
      columns {
        ...Column
      }
      rows {
        ...Record
      }
    }
  }

  ${textFragment}
  ${recordFragment}
  ${columnFragment}
`;
