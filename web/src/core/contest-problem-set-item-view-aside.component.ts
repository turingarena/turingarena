import { Component, Input, ViewEncapsulation } from '@angular/core';
import gql from 'graphql-tag';
import { ContestProblemSetItemViewAsideFragment } from '../generated/graphql-types';
import { gradingStateFragment } from './grading.component';
import { mediaDownloadFragment } from './media-download.component';
import { mediaInlineFragment } from './media-inline.component';
import { textFragment } from './text.pipe';

@Component({
  selector: 'app-contest-problem-set-item-view-aside',
  templateUrl: './contest-problem-set-item-view-aside.component.html',
  styleUrls: ['./contest-problem-set-item-view-aside.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class ContestProblemSetItemViewAsideComponent {
  @Input()
  data!: ContestProblemSetItemViewAsideFragment;
}

export const contestProblemSetItemViewAsideFragment = gql`
  fragment ContestProblemSetItemViewAside on ContestProblemSetItemView {
    item {
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

    awardSetItemViews {
      item {
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
  }

  ${textFragment}
  ${mediaInlineFragment}
  ${mediaDownloadFragment}
  ${gradingStateFragment}
`;
