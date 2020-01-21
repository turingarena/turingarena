import { Component } from '@angular/core';
import { Apollo } from 'apollo-angular';
import gql from 'graphql-tag';
import { ContestQuery, ContestQueryVariables } from '../../generated/graphql-types';

@Component({
  selector: 'app-contest-view',
  templateUrl: './contest-view.component.html',
  styleUrls: ['./contest-view.component.scss'],
})
export class ContestViewComponent {
  constructor(private readonly apollo: Apollo) {}

  contestQuery = this.apollo.watchQuery<ContestQuery, ContestQueryVariables>({
    query: gql`
      query Contest {
        contest(name: "contest1") {
          name
        }
      }
    `,
  });
}
