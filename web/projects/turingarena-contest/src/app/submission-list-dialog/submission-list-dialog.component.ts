import { Component, Input, OnInit } from '@angular/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { QueryRef } from 'apollo-angular';
import { AppComponent } from '../app.component';
import { SubmissionDialogComponent } from '../submission-dialog/submission-dialog.component';
import { SubmissionListQueryService } from '../submission-list-query.service';
import { SubmissionQueryService } from '../submission-query.service';
import {
  SubmissionListQuery,
  SubmissionListQueryVariables,
  SubmissionListQuery_user_problem_submissions as Submission,
} from '../__generated__/SubmissionListQuery';
import { ContestQuery_user_problems_material_scorables as Scorable } from '../__generated__/ContestQuery';

@Component({
  selector: 'app-submission-list-dialog',
  templateUrl: './submission-list-dialog.component.html',
  styleUrls: ['./submission-list-dialog.component.scss']
})
export class SubmissionListDialogComponent implements OnInit {

  constructor(
    private modal: NgbModal,
    private submissionListQueryService: SubmissionListQueryService,
    private submissionQueryService: SubmissionQueryService,
  ) { }

  @Input()
  appComponent: AppComponent;

  @Input()
  problemName: string;

  submissionListQuery: QueryRef<SubmissionListQuery, SubmissionListQueryVariables>;

  ngOnInit() {
    this.submissionListQuery = this.submissionListQueryService.watch({
      userId: 'test', // FIXME
      problemName: this.problemName,
    });
  }

  getState(scorable: Scorable, submission: Submission) {
    return submission.scores.find((s) => s.scorableId === scorable.name) || { score: 0 };
  }

  async openDetail(submission: Submission) {
    const modalRef = this.modal.open(SubmissionDialogComponent);
    const modal = modalRef.componentInstance;

    modal.appComponent = this.appComponent;
    modal.problemName = this.problemName;
    modal.setSubmissionQueryRef(this.submissionQueryService.watch({
      submissionId: submission.id,
    }));

    try {
      await modalRef.result;
    } catch (e) {
      // No-op
    }
  }

}
