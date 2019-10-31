import { Component, Input, OnInit } from '@angular/core';
import { faSpinner } from '@fortawesome/free-solid-svg-icons';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { QueryRef } from 'apollo-angular';
import { Duration } from 'luxon';

import { ContestQuery_contestView_problems as Problem } from '../__generated__/ContestQuery';
import {
  SubmissionQuery,
  SubmissionQuery_submission,
  SubmissionQuery_submission_evaluationEvents_event_ValueEvent_value as Value,
  SubmissionQueryVariables,
} from '../__generated__/SubmissionQuery';
import { SubmissionQueryService } from '../submission-query.service';
import { ScoreRangeFragment } from '../__generated__/ScoreRangeFragment';

@Component({
  selector: 'app-submission-dialog',
  templateUrl: './submission-dialog.component.html',
  styleUrls: ['./submission-dialog.component.scss'],
})
export class SubmissionDialogComponent implements OnInit {
  constructor(
    private readonly submissionQueryService: SubmissionQueryService,
  ) { }

  faSpinner = faSpinner;

  @Input()
  submissionId!: string;

  @Input()
  problem!: Problem;

  @Input()
  modal!: NgbActiveModal;

  submissionQueryRef!: QueryRef<SubmissionQuery, SubmissionQueryVariables>;

  ngOnInit() {
    const { submissionId } = this;
    this.submissionQueryRef = this.submissionQueryService.watch(
      { submissionId }, { pollInterval: 1000 });
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
    const precision = 3;
    const duration = Duration.fromObject({ seconds });
    if (seconds < 1) {
      return `${duration.as('milliseconds').toPrecision(precision)} ms`;
    } else {
      return `${duration.as('seconds').toPrecision(precision)} s`;
    }
  }

  getValence(value?: Value) {
    if (value === undefined) { return 'unknown'; }
    if (value.__typename !== 'ValenceValue') { throw new Error(); }

    return value.valence.toLowerCase();
  }

  // FIXME: type this correctly
  getScoreValence(value: Value | undefined, range: ScoreRangeFragment) {
    if (value === undefined) { return 'unknown'; }
    if (value.__typename !== 'ScoreValue') { throw new Error(); }

    const { score } = value;
    if (score <= 0) { return 'failure'; }
    if (score < range.max) { return 'partial'; }

    return 'success';
  }
}
