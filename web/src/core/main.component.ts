import { Component } from '@angular/core';
import { Apollo } from 'apollo-angular';
import gql from 'graphql-tag';
import { MainViewQuery, MainViewQueryVariables } from '../generated/graphql-types';
import { mainViewFragment } from './main-view.component';

@Component({
  selector: 'app-main',
  templateUrl: './main.component.html',
  styleUrls: ['./main.component.scss'],
})
export class MainComponent {
  constructor(private readonly apollo: Apollo) {}

  readonly queryRef = this.apollo.watchQuery<MainViewQuery, MainViewQueryVariables>({
    query: gql`
      query MainView {
        mainView {
          ...MainView
        }
      }

      ${mainViewFragment}
    `,
  });
}
