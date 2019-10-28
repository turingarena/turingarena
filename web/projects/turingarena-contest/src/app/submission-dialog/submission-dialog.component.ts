import { Component, Input, OnInit } from '@angular/core';
import { NgbModal, NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { QueryRef } from 'apollo-angular';
import { AppComponent } from '../app.component';
import {
  SubmissionQuery,
  SubmissionQueryVariables,
  SubmissionQuery_submission_evaluationEvents_event_ValueEvent_value as Value,
} from '../__generated__/SubmissionQuery';
import { SubmissionQueryService } from '../submission-query.service';
import { ContestQuery_contestView_problems as Problem } from '../__generated__/ContestQuery';

@Component({
  selector: 'app-submission-dialog',
  templateUrl: './submission-dialog.component.html',
  styleUrls: ['./submission-dialog.component.scss']
})
export class SubmissionDialogComponent implements OnInit {
  constructor(
    private submissionQueryService: SubmissionQueryService,
  ) { }

  @Input()
  submissionId: string;

  @Input()
  problem: Problem;

  @Input()
  modal: NgbActiveModal;

  submissionQueryRef: QueryRef<SubmissionQuery, SubmissionQueryVariables>;

  ngOnInit() {
    const { submissionId } = this;
    this.submissionQueryRef = this.submissionQueryService.watch({
      submissionId,
    }, {
        pollInterval: 1000,
      });
  }

  getEvaluationRecord(data: SubmissionQuery) {
    const record: Record<string, Value> = {};
    for (const event of data.submission.evaluationEvents) {
      if (event.event.__typename === 'ValueEvent') {
        const { key, value } = event.event;
        record[key] = value;
      }
    }
    return record;
  }

}
