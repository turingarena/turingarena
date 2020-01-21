import { Component, Input, ViewEncapsulation } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import gql from 'graphql-tag';
import { ContestViewFragment } from '../generated/graphql-types';
import { contestProblemSetItemViewAsideFragment } from './contest-problem-set-item-view-aside.component';
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
      itemViews {
        item {
          problem {
            name
            statement {
              ...MediaInline
            }
          }
        }
        ...ContestProblemSetItemViewAside
      }
    }

    ...ContestViewAside
  }

  ${textFragment}
  ${mediaInlineFragment}
  ${contestViewAsideFragment}
  ${contestProblemSetItemViewAsideFragment}
`;
