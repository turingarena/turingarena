import { Component, Input, ViewEncapsulation } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import gql from 'graphql-tag';
import { ContestViewFragment } from '../generated/graphql-types';
import { contestProblemAssignmentViewAsideFragment } from './contest-problem-assignment-view-aside.component';
import { contestViewAsideFragment } from './contest-view-aside.component';
import { mediaInlineFragment } from './media-inline.component';
import { textFragment } from './text.pipe';

@Component({
  selector: 'app-contest-view',
  templateUrl: './contest-view.component.html',
  styleUrls: ['./contest-view.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class ContestViewComponent {
  @Input()
  data!: ContestViewFragment;

  constructor(readonly route: ActivatedRoute) {}
}

export const contestViewFragment = gql`
  fragment ContestView on ContestView {
    contest {
      title {
        ...Text
      }
    }

    problemSetView {
      assignmentViews {
        assignment {
          problem {
            name
            statement {
              ...MediaInline
            }
          }
        }
        ...ContestProblemAssignmentViewAside
      }
    }

    ...ContestViewAside
  }

  ${textFragment}
  ${mediaInlineFragment}
  ${contestViewAsideFragment}
  ${contestProblemAssignmentViewAsideFragment}
`;
