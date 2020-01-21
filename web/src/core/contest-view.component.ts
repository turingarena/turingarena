import { Component, Input, ViewEncapsulation } from '@angular/core';
import gql from 'graphql-tag';
import { ContestViewFragment } from '../generated/graphql-types';
import { contestProblemSetItemViewAsideFragment } from './contest-problem-set-item-view-aside.component';
import { contestViewAsideFragment } from './contest-view-aside.component';
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
        ...ContestProblemSetItemViewAside
      }
    }

    ...ContestViewAside
  }

  ${textFragment}
  ${contestViewAsideFragment}
  ${contestProblemSetItemViewAsideFragment}
`;
