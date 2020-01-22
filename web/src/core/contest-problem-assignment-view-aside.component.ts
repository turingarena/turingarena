import { Component, Input, ViewEncapsulation } from '@angular/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import gql from 'graphql-tag';
import { ContestProblemAssignmentViewAsideFragment } from '../generated/graphql-types';
import { contestProblemAssignmentViewSubmitModalFragment } from './contest-problem-assignment-view-submit-modal.component';
import { gradingStateFragment } from './grading.component';
import { mediaDownloadFragment } from './media-download.component';
import { mediaInlineFragment } from './media-inline.component';
import { textFragment } from './text.pipe';

@Component({
  selector: 'app-contest-problem-assignment-view-aside',
  templateUrl: './contest-problem-assignment-view-aside.component.html',
  styleUrls: ['./contest-problem-assignment-view-aside.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class ContestProblemAssignmentViewAsideComponent {
  constructor(readonly modalService: NgbModal) {}

  @Input()
  data!: ContestProblemAssignmentViewAsideFragment;
}

export const contestProblemAssignmentViewAsideFragment = gql`
  fragment ContestProblemAssignmentViewAside on ContestProblemAssignmentView {
    assignment {
      problem {
        name
        title {
          ...Text
        }
        statement {
          ...MediaInline
          ...MediaDownload
        }
        attachments {
          title {
            ...Text
          }
          media {
            ...MediaDownload
          }
        }
      }
    }

    canSubmit
    submissions {
      id
    }

    gradingState {
      ...GradingState
    }

    awardAssignmentViews {
      assignment {
        award {
          name
          title {
            ...Text
          }
        }
      }

      gradingState {
        ...GradingState
      }
    }

    ...ContestProblemAssignmentViewSubmitModal
  }

  ${textFragment}
  ${mediaInlineFragment}
  ${mediaDownloadFragment}
  ${gradingStateFragment}
  ${contestProblemAssignmentViewSubmitModalFragment}
`;
