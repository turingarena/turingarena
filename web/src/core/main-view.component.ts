import { Component, Input } from '@angular/core';
import gql from 'graphql-tag';
import { MainViewFragment } from '../generated/graphql-types';
import { contestViewFragment } from './contest-view.component';

@Component({
  selector: 'app-main-view',
  templateUrl: './main-view.component.html',
  styleUrls: ['./main-view.component.scss'],
})
export class MainViewComponent {
  @Input()
  data!: MainViewFragment;
}

export const mainViewFragment = gql`
  fragment MainView on MainView {
    contestView {
      ...ContestView
    }
  }

  ${contestViewFragment}
`;
