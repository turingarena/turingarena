import { Component, ViewEncapsulation } from '@angular/core';
import { Apollo } from 'apollo-angular';
import gql from 'graphql-tag';
import { MainViewQuery, MainViewQueryVariables } from '../generated/graphql-types';
import { mainViewFragment } from './main-view.component';

@Component({
  selector: 'app-main',
  templateUrl: './main.component.html',
  styleUrls: ['./main.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class MainComponent {
  constructor(private readonly apollo: Apollo) {}

  readonly queryRef = this.apollo.watchQuery<MainViewQuery, MainViewQueryVariables>({
    query: gql`
      query MainView {
        mainView(username: "user1") {
          ...MainView
        }
      }

      ${mainViewFragment}
    `,
  });
}
