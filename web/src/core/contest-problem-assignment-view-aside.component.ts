import { Component, Input, ViewEncapsulation } from '@angular/core';
import gql from 'graphql-tag';
import { ContestProblemAssignmentViewAsideFragment } from '../generated/graphql-types';
import { contestProblemUserTacklingAsideFragment } from './contest-problem-user-tackling-aside.component';
import { gradeVariableFragment } from './grading/grade-variable.component';
import { scoreVariableFragment } from './grading/score-variable.component';
import { mediaDownloadFragment } from './material/media-download.component';
import { mediaInlineFragment } from './material/media-inline.component';
import { textFragment } from './material/text.pipe';

@Component({
  selector: 'app-contest-problem-assignment-view-aside',
  templateUrl: './contest-problem-assignment-view-aside.component.html',
  styleUrls: ['./contest-problem-assignment-view-aside.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class ContestProblemAssignmentViewAsideComponent {
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

    totalScoreVariable {
      ...ScoreVariable
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

      gradeVariable {
        ...GradeVariable
      }
    }

    tackling {
      ...ContestProblemUserTacklingAside
    }
  }

  ${textFragment}
  ${mediaInlineFragment}
  ${mediaDownloadFragment}
  ${scoreVariableFragment}
  ${gradeVariableFragment}
  ${contestProblemUserTacklingAsideFragment}
`;
