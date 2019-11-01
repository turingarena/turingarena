import { Component, Input, OnInit } from '@angular/core';
import { NgbActiveModal, NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { QueryRef } from 'apollo-angular';

import {
  SubmissionListQuery,
  SubmissionListQueryVariables,
} from '../__generated__/SubmissionListQuery';
import { scoreRanges } from '../problem-material';
import { SubmissionListQueryService } from '../submission-list-query.service';
import { ProblemMaterialFragment } from '../__generated__/ProblemMaterialFragment';
import { SubmissionFragment } from '../__generated__/SubmissionFragment';
import { ProblemTacklingFragment } from '../__generated__/ProblemTacklingFragment';
import { getProblemState } from '../problem';
import { getSubmissionState } from '../submission';

@Component({
  selector: 'app-submission-list-dialog',
  templateUrl: './submission-list-dialog.component.html',
  styleUrls: ['./submission-list-dialog.component.scss'],
})
export class SubmissionListDialogComponent implements OnInit {

  constructor(
    readonly modalService: NgbModal,
    private readonly submissionListQueryService: SubmissionListQueryService,
  ) { }

  @Input()
  userId!: string;

  @Input()
  problemName!: string;

  @Input()
  modal!: NgbActiveModal;

  submissionListQuery!: QueryRef<SubmissionListQuery, SubmissionListQueryVariables>;

  getProblemState = getProblemState;
  getSubmissionState = getSubmissionState;

  ngOnInit() {
    const { userId, problemName } = this;
    this.submissionListQuery = this.submissionListQueryService
      .watch({ userId, problemName }, { pollInterval: 1000 });
  }

}
