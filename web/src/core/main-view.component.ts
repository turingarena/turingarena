import { Component, Input, ViewEncapsulation } from '@angular/core';
import gql from 'graphql-tag';
import { MainViewFragment } from '../generated/graphql-types';
import { contestViewFragment } from './contest-view.component';
import { textFragment } from './material/text.pipe';

@Component({
  selector: 'app-main-view',
  templateUrl: './main-view.component.html',
  styleUrls: ['./main-view.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class MainViewComponent {
  @Input()
  data!: MainViewFragment;
}

export const mainViewFragment = gql`
  fragment MainView on MainView {
    title {
      ...Text
    }
    contestView {
      ...ContestView
    }
  }

  ${textFragment}
  ${contestViewFragment}
`;
