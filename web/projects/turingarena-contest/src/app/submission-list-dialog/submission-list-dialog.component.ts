import { Component, Input, OnInit } from '@angular/core';
import { NgbActiveModal, NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { QueryRef } from 'apollo-angular';
import { SubmissionListQueryService } from '../submission-list-query.service';
import {
  SubmissionListQuery,
  SubmissionListQueryVariables,
  SubmissionListQuery_contestView_problem_submissions as Submission,
  SubmissionListQuery_contestView_problem as Problem,
} from '../__generated__/SubmissionListQuery';
import { scoreRanges } from '../problem-material';

@Component({
  selector: 'app-submission-list-dialog',
  templateUrl: './submission-list-dialog.component.html',
  styleUrls: ['./submission-list-dialog.component.scss']
})
export class SubmissionListDialogComponent implements OnInit {

  constructor(
    readonly modalService: NgbModal,
    private submissionListQueryService: SubmissionListQueryService,
  ) { }

  @Input()
  userId: string;

  @Input()
  problemName: string;

  @Input()
  modal: NgbActiveModal;

  submissionListQuery: QueryRef<SubmissionListQuery, SubmissionListQueryVariables>;

  ngOnInit() {
    this.submissionListQuery = this.submissionListQueryService.watch({
      userId: this.userId,
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
      award({ name }) {
        // FIXME: repeated code
        const scoreState = submission.scores.find((s) => s.awardName === name);
        const badgeState = submission.badges.find((s) => s.awardName === name);
        return {
          score: scoreState ? scoreState.score : 0,
          badge: badgeState ? badgeState.badge : false,
        };
      },
    };
  }

  getProblemState(problem: Problem) {
    return {
      award({ name }) {
        // FIXME: repeated code
        const scoreState = problem.scores.find((s) => s.awardName === name);
        const badgeState = problem.badges.find((s) => s.awardName === name);
        return {
          score: scoreState ? scoreState.score : 0,
          badge: badgeState ? badgeState.badge : false,
        };
      },
      maxScore: scoreRanges(problem).map(({ range: { max } }) => max).reduce((a, b) => a + b, 0),
      precision: scoreRanges(problem).map(({ range: { precision } }) => precision).reduce((a, b) => Math.max(a, b)),
      score: scoreRanges(problem)
        .map(({ name }) => problem.scores.find((s) => s.awardName === name))
        .map((state) => state ? state.score as number : 0)
        .reduce((a, b) => a + b, 0),
    };
  }

}
