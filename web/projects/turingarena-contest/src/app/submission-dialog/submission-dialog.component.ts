import { Component, Input, OnInit } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { QueryRef } from 'apollo-angular';
import {
  SubmissionQuery,
  SubmissionQueryVariables,
  SubmissionQuery_submission_evaluationEvents_event_ValueEvent_value as Value,
  SubmissionQuery_submission,
} from '../__generated__/SubmissionQuery';
import { SubmissionQueryService } from '../submission-query.service';
import { ContestQuery_contestView_problems as Problem } from '../__generated__/ContestQuery';
import { faSpinner } from '@fortawesome/free-solid-svg-icons';
import { Duration } from 'luxon';

@Component({
  selector: 'app-submission-dialog',
  templateUrl: './submission-dialog.component.html',
  styleUrls: ['./submission-dialog.component.scss']
})
export class SubmissionDialogComponent implements OnInit {
  constructor(
    private submissionQueryService: SubmissionQueryService,
  ) { }

  faSpinner = faSpinner;

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

  getEvaluationRecord(submission: SubmissionQuery_submission) {
    const record: Record<string, Value> = {};
    for (const event of submission.evaluationEvents) {
      if (event.event.__typename === 'ValueEvent') {
        const { key, value } = event.event;
        record[key] = value;
      }
    }
    return record;
  }

  displayTimeSeconds(seconds: number) {
    if (seconds < 1) {
      return `${(seconds * 1000).toPrecision(3)} ms`;
    } else {
      return `${seconds.toPrecision(3)} s`;
    }
  }

}
