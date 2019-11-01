import { Component, Input, OnInit } from '@angular/core';
import { NgbActiveModal, NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { QueryRef, Apollo } from 'apollo-angular';

import {
  SubmissionListQuery,
  SubmissionListQueryVariables,
} from '../__generated__/SubmissionListQuery';
import { problemMaterialFragment } from '../problem-material';
import { getProblemState, problemFragment } from '../problem';
import { getSubmissionState, submissionFragment } from '../submission';
import gql from 'graphql-tag';

@Component({
  selector: 'app-submission-list-dialog',
  templateUrl: './submission-list-dialog.component.html',
  styleUrls: ['./submission-list-dialog.component.scss'],
})
export class SubmissionListDialogComponent implements OnInit {

  constructor(
    readonly modalService: NgbModal,
    private readonly apollo: Apollo,
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
    this.submissionListQuery = this.apollo.watchQuery({
      query: gql`
        query SubmissionListQuery($userId: UserId!, $problemName: ProblemName!) {
          contestView(userId: $userId) {
            user {
              id
            }
            problem(name: $problemName) {
              ...ProblemMaterialFragment
              tackling {
                ...ProblemTacklingFragment
                submissions { ...SubmissionFragment }
              }
            }
          }
        }
        ${problemMaterialFragment}
        ${problemFragment}
        ${submissionFragment}
      `,
      variables: { userId, problemName },
      pollInterval: 1000,
    });
  }

}
