import { Component, Input, OnInit } from '@angular/core';
import { faSpinner } from '@fortawesome/free-solid-svg-icons';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { QueryRef } from 'apollo-angular';
import { Duration } from 'luxon';

import {
  SubmissionQuery,
  SubmissionQueryVariables,
} from '../__generated__/SubmissionQuery';
import { SubmissionQueryService } from '../submission-query.service';
import { ScoreRangeFragment } from '../__generated__/ScoreRangeFragment';
import { SubmissionEvaluationFragment } from '../__generated__/SubmissionEvaluationFragment';
import { ProblemMaterialFragment } from '../__generated__/ProblemMaterialFragment';
import { ValueFragment } from '../__generated__/ValueFragment';
import { ValenceValueFragment } from '../__generated__/ValenceValueFragment';
import { ScoreValueFragment } from '../__generated__/ScoreValueFragment';

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
  problem!: ProblemMaterialFragment;

  @Input()
  modal!: NgbActiveModal;

  submissionQueryRef!: QueryRef<SubmissionQuery, SubmissionQueryVariables>;

  ngOnInit() {
    const { submissionId } = this;
    this.submissionQueryRef = this.submissionQueryService.watch(
      { submissionId }, { pollInterval: 1000 });
  }

  getEvaluationRecord(submission: SubmissionEvaluationFragment) {
    const record: Record<string, ValueFragment> = {};
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

  getValence(value?: ValenceValueFragment) {
    if (value === undefined) { return 'unknown'; }

    return value.valence.toLowerCase();
  }

  // FIXME: type this correctly
  getScoreValence(value: ScoreValueFragment | undefined, range: ScoreRangeFragment) {
    if (value === undefined) { return 'unknown'; }

    const { score } = value;
    if (score <= 0) { return 'failure'; }
    if (score < range.max) { return 'partial'; }

    return 'success';
  }
}
