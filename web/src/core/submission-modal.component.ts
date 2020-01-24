import { Component, Input, ViewEncapsulation } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import gql from 'graphql-tag';
import { SubmissionModalFragment } from '../generated/graphql-types';
import { textFragment } from './text.pipe';

@Component({
  selector: 'app-submission-modal',
  templateUrl: './submission-modal.component.html',
  styleUrls: ['./submission-modal.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class SubmissionModalComponent {
  @Input()
  modal!: NgbActiveModal;

  @Input()
  data!: SubmissionModalFragment;
}

export const submissionModalFragment = gql`
  fragment SubmissionModal on Submission {
    # TODO: files
    createdAt
    officialEvaluation {
      status
    }
    problem {
      title {
        ...Text
      }
    }
  }

  ${textFragment}
`;
