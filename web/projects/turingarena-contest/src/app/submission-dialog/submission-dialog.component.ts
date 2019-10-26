import { Component } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { QueryRef } from 'apollo-angular';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { AppComponent } from '../app.component';
import {
  SubmissionQuery,
  SubmissionQueryVariables,
  SubmissionQuery_submission_evaluationEvents_event_ValueEvent_value as Value,
} from '../__generated__/SubmissionQuery';

@Component({
  selector: 'app-submission-dialog',
  templateUrl: './submission-dialog.component.html',
  styleUrls: ['./submission-dialog.component.scss']
})
export class SubmissionDialogComponent {
  constructor(readonly activeModal: NgbActiveModal) { }

  submissionQueryRef: QueryRef<SubmissionQuery, SubmissionQueryVariables>;
  recordObservable: Observable<Record<string, Value>>;

  appComponent: AppComponent;
  problemName: string;

  setSubmissionQueryRef(submissionQueryRef: QueryRef<SubmissionQuery, SubmissionQueryVariables>) {
    this.submissionQueryRef = submissionQueryRef;
    this.recordObservable = this.submissionQueryRef.valueChanges.pipe(
      map((result) => {
        if (result.data === undefined) { return {}; }

        const record: Record<string, Value> = {};
        for (const event of result.data.submission.evaluationEvents) {
          if (event.event.__typename === 'ValueEvent') {
            const { key, value } = event.event;
            record[key] = value;
          }
        }
        return record;
      })
    );
  }

}
