import { Component, Input, ViewEncapsulation } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import gql from 'graphql-tag';
import { ContestProblemAssignmentViewSubmitModalFragment } from '../generated/graphql-types';
import { textFragment } from './text.pipe';

@Component({
  selector: 'app-contest-problem-assignment-view-submit-modal',
  templateUrl: './contest-problem-assignment-view-submit-modal.component.html',
  styleUrls: ['./contest-problem-assignment-view-submit-modal.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class ContestProblemAssignmentViewSubmitModalComponent {
  @Input()
  modal!: NgbActiveModal;

  @Input()
  data!: ContestProblemAssignmentViewSubmitModalFragment;
}

export const contestProblemAssignmentViewSubmitModalFragment = gql`
  fragment ContestProblemAssignmentViewSubmitModal on ContestProblemAssignmentView {
    assignment {
      problem {
        name
        title {
          ...Text
        }
      }
    }
  }

  ${textFragment}
`;
