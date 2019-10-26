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
  SubmissionListQuery_contestView_problem_submissions as Submission,
  SubmissionListQuery_contestView_problem as Problem,
} from '../__generated__/SubmissionListQuery';
import { ContestQuery_contestView_problems_material_awards as Award } from '../__generated__/ContestQuery';
import { scoreRanges } from '../problem-material';

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
    const { userId } = this.appComponent;
    this.submissionListQuery = this.submissionListQueryService.watch({
      userId,
      problemName: this.problemName,
    }, {
        fetchPolicy: 'cache-and-network',
        pollInterval: 1000,
      });
  }

  getSubmissionState(problem: Problem, submission: Submission) {
    return {
      score: problem.material.awards
        .map((award) => submission.scores.find((s) => s.awardName === award.name))
        .map((state) => state ? state.score as number : 0)
        .reduce((a, b) => a + b, 0),
      award(award: Award) {
        return submission.scores.find((s) => s.awardName === award.name) || { score: 0 };
      },
    };
  }

  getProblemState(problem: Problem) {
    return {
      award(award: Award) {
        return problem.scores.find((s) => s.awardName === award.name) || { score: 0 };
      },
      maxScore: scoreRanges(problem).map(({ range: { max } }) => max).reduce((a, b) => a + b, 0),
      precision: scoreRanges(problem).map(({ range: { precision } }) => precision).reduce((a, b) => Math.max(a, b)),
      score: scoreRanges(problem)
        .map(({ name }) => problem.scores.find((s) => s.awardName === name))
        .map((state) => state ? state.score as number : 0)
        .reduce((a, b) => a + b, 0),
    };
  }

  async openDetail(submission: Submission) {
    const modalRef = this.modal.open(SubmissionDialogComponent, { size: 'lg' });
    const modal = modalRef.componentInstance;

    modal.appComponent = this.appComponent;
    modal.problemName = this.problemName;
    modal.setSubmissionQueryRef(this.submissionQueryService.watch({
      submissionId: submission.id,
    }, {
        pollInterval: 1000,
      }));

    try {
      await modalRef.result;
    } catch (e) {
      // No-op
    }
  }

}
